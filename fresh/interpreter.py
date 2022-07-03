from fresh.errors import RTError
from fresh.runtimeresult import RuntimeResult
from fresh.values import Number, Function, String, List
from fresh.tokens import *


class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    def visit_NumberNode(self, node, context):
        return RuntimeResult().success(Number(node.token.value).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_VariableAccessNode(self, node, context):
        response = RuntimeResult()
        variable_name = node.variable_name_token.value
        value = context.symbol_table.get(variable_name)
        if not value:
            return response.failure(RTError(node.pos_start, node.pos_end, f'{variable_name} is not defined.', context))

        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return response.success(value)

    def visit_VariableAssignNode(self, node, context):
        response = RuntimeResult()
        variable_name = node.token.value
        value = response.register(self.visit(node.value_node, context))
        if response.should_return():
            return response
        if isinstance(value, List):
            value = value.copy_as_true_new()
        context.symbol_table.set(variable_name, value)
        return response.success(value)

    def visit_BinOpNode(self, node, context):
        response = RuntimeResult()
        error = None
        result = None
        left_node = response.register(self.visit(node.left_node, context))
        if response.should_return():
            return response
        right_node = response.register(self.visit(node.right_node, context))
        if response.should_return():
            return response

        if node.operator_token.type == TT_PLUS:
            result, error = left_node.added_to(right_node)
        elif node.operator_token.type == TT_MINUS:
            result, error = left_node.subtracted_by(right_node)
        elif node.operator_token.type == TT_MUL:
            result, error = left_node.multiplied_by(right_node)
        elif node.operator_token.type == TT_DIV:
            result, error = left_node.divided_by(right_node)
        elif node.operator_token.type == TT_POW:
            result, error = left_node.powered_by(right_node)
        elif node.operator_token.type == TT_DOUBLEEQUALS:
            result, error = left_node.get_comparison_equals(right_node)
        elif node.operator_token.type == TT_NOTEQUALS:
            result, error = left_node.get_comparison_notequals(right_node)
        elif node.operator_token.type == TT_GREATER:
            result, error = left_node.get_comparison_greaterthan(right_node)
        elif node.operator_token.type == TT_GREATEREQUALS:
            result, error = left_node.get_comparison_greaterequals(right_node)
        elif node.operator_token.type == TT_LESS:
            result, error = left_node.get_comparison_lessthan(right_node)
        elif node.operator_token.type == TT_LESSEQUALS:
            result, error = left_node.get_comparison_lessequals(right_node)
        elif node.operator_token.matches(TT_KEYWORD, 'and'):
            result, error = left_node.anded_by(right_node)
        elif node.operator_token.matches(TT_KEYWORD, 'or'):
            result, error = left_node.ored_by(right_node)
        elif node.operator_token.type == TT_QUESTIONMARK:
            result, error = left_node.query_by(right_node)

        if error:
            return response.failure(error)
        return response.success(result.set_pos(node.pos_start, node.pos_end).set_context(context))

    def visit_UnaryOpNode(self, node, context):
        response = RuntimeResult()
        number = response.register(self.visit(node.node, context))
        if response.should_return():
            return response

        error = None

        if node.operator_token.type == TT_MINUS:
            number, error = number.multiplied_by(Number(-1))
        elif node.operator_token.matches(TT_KEYWORD, 'not'):
            number, error = number.notted()

        if error:
            return response.failure(error)
        else:
            return response.success(number.set_pos(node.pos_start, node.pos_end).set_context(context))

    def visit_IfNode(self, node, context):
        response = RuntimeResult()

        for condition, expression, should_return_null in node.cases:
            condition_value = response.register(self.visit(condition, context))
            if response.should_return():
                return response

            if condition_value.is_true():
                expression_value = response.register(self.visit(expression, context))
                if response.should_return():
                    return response
                return response.success(Number.null if should_return_null else expression_value)

        if node.else_case:
            expression, should_return_null = node.else_case
            else_value = response.register(self.visit(expression, context))
            if response.should_return():
                return response
            return response.success(Number.null if should_return_null else else_value)

        return response.success(Number.null)

    def visit_ForNode(self, node, context):
        response = RuntimeResult()
        elements = []

        start_value = response.register(self.visit(node.start_value_node, context))
        if response.should_return():
            return response

        end_value = response.register(self.visit(node.end_value_node, context))
        if response.should_return():
            return response

        if node.step_value_node:
            step_value = response.register(self.visit(node.step_value_node, context))
            if response.should_return():
                return response
        else:
            step_value = Number(1)

        i = start_value.value

        if step_value.value >= 0:
            condition = lambda: i < end_value.value
        else:
            condition = lambda: i > end_value.value

        while condition():
            context.symbol_table.set(node.variable_name_token.value, Number(i))
            i += step_value.value

            value = response.register(self.visit(node.body_node, context))
            if response.should_return() and response.loop_should_continue == False and response.loop_should_break == False:
                return response

            if response.loop_should_continue:
                continue

            if response.loop_should_break:
                break

            elements.append(value)

        return response.success(
            Number.null if node.should_return_null else
            List(elements).set_pos(node.pos_start, node.pos_end).set_context(context)
        )

    def visit_WhileNode(self, node, context):
        response = RuntimeResult()
        elements = []

        while True:
            condition = response.register(self.visit(node.condition_node, context))
            if response.should_return():
                return response

            if not condition.is_true():
                break

            value = response.register(self.visit(node.body_node, context))
            if response.should_return() and response.loop_should_continue == False and response.loop_should_break == False:
                return response

            if response.loop_should_continue:
                continue

            if response.loop_should_break:
                break

        return response.success(
            Number.null if node.should_return_null else
            List(elements).set_pos(node.pos_start, node.pos_end).set_context(context)
        )

    def visit_FunctionDefinitionNode(self, node, context):
        response = RuntimeResult()

        function_name = node.variable_name_token.value if node.variable_name_token else None
        body_node = node.body_node
        arguments = [argument.value for argument in node.argument_name_tokens]
        function_value = Function(function_name, body_node, arguments, node.should_auto_return).set_context(context).set_pos(node.pos_start, node.pos_end)

        if node.variable_name_token:
            context.symbol_table.set(function_name, function_value)

        return response.success(function_value)

    def visit_CallNode(self, node, context):
        response = RuntimeResult()
        try:
            arguments = []

            value_to_call = response.register(self.visit(node.function_node, context))
            if response.should_return():
                return response
            value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end).set_context(context)

            for argument_node in node.argument_nodes:
                argument = response.register(self.visit(argument_node, context))
                if response.should_return():
                    return response
                arguments.append(argument)

            return_value = response.register(value_to_call.execute(arguments))
            if response.should_return():
                return response
            return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
            return response.success(return_value)
        except RecursionError:
            value_to_call = response.register(self.visit(node.function_node, context))
            return response.failure(RTError(
                value_to_call.pos_start,
                value_to_call.pos_end,
                'Max recursion depth exceeded',
                context
            ))

    def visit_StringNode(self, node, context):
        return RuntimeResult().success(String(node.token.value).set_pos(node.pos_start, node.pos_end).set_context(context))

    def visit_ListNode(self, node, context):
        response = RuntimeResult()
        elements = []

        for element_node in node.element_nodes:
            element = response.register(self.visit(element_node, context))
            if response.should_return():
                return response
            elements.append(element)

        return response.success(List(elements).set_pos(node.pos_start, node.pos_end).set_context(context))

    def visit_ReturnNode(self, node, context):
        response = RuntimeResult()

        if node.node_to_return:
            value = response.register(self.visit(node.node_to_return, context))
            if response.should_return():
                return response
        else:
            value = Number.null

        return response.success_return(value)

    def visit_ContinueNode(self, node, context):
        return RuntimeResult().success_continue()

    def visit_BreakNode(self, node, context):
        return RuntimeResult().success_break()
