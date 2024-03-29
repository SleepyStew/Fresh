class NumberNode:
    def __init__(self, token):
        self.token = token
        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end

    def __repr__(self):
        return f'{self.token}'


class StringNode:
    def __init__(self, token):
        self.token = token
        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end

    def __repr__(self):
        return f'{self.token}'


class BinOpNode:
    def __init__(self, left_node, operator_token, right_node):
        self.left_node = left_node
        self.operator_token = operator_token
        self.right_node = right_node
        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.operator_token}, {self.right_node})'


class UnaryOpNode:
    def __init__(self, operator_token, right_node):
        self.operator_token = operator_token
        self.node = right_node

        self.pos_start = self.operator_token.pos_start
        self.pos_end = self.node.pos_end

    def __repr__(self):
        return f'({self.operator_token}, {self.node})'


class VariableAccessNode:
    def __init__(self, variable_name_token):
        self.variable_name_token = variable_name_token
        self.pos_start = self.variable_name_token.pos_start
        self.pos_end = self.variable_name_token.pos_end

    def __repr__(self):
        return f'{self.variable_name_token}'


class VariableAssignNode:
    def __init__(self, token, value_node):
        self.token = token
        self.value_node = value_node
        self.pos_start = self.token.pos_start
        self.pos_end = self.value_node.pos_end

    def __repr__(self):
        return f'({self.token}, {self.value_node})'


class IfNode:
    def __init__(self, cases, else_case):
        self.cases = cases
        self.else_case = else_case
        self.pos_start = self.cases[0][0].pos_start
        self.pos_end = (self.else_case or self.cases[len(self.cases) - 1])[0].pos_end


class ForNode:
    def __init__(self, variable_name_token, start_value_node, end_value_node, step_value_node, body_node, should_return_null):
        self.variable_name_token = variable_name_token
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node
        self.should_return_null = should_return_null

        self.pos_start = self.variable_name_token.pos_start
        self.pos_end = self.body_node.pos_end


class WhileNode:
    def __init__(self, condition_node, body_node, should_return_null):
        self.condition_node = condition_node
        self.body_node = body_node
        self.should_return_null = should_return_null

        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end


class FunctionDefinitionNode:
    def __init__(self, variable_name_token, argument_name_tokens, body_node, should_auto_return):
        self.variable_name_token = variable_name_token
        self.argument_name_tokens = argument_name_tokens
        self.body_node = body_node
        self.should_auto_return = should_auto_return

        if self.variable_name_token:
            self.pos_start = self.variable_name_token.pos_start
        elif len(self.argument_name_tokens) > 0:
            self.pos_start = self.argument_name_tokens[0].pos_start
        else:
            self.pos_start = self.body_node.pos_start

        self.pos_end = self.body_node.pos_end


class CallNode:
    def __init__(self, function_node, argument_nodes):
        self.function_node = function_node
        self.argument_nodes = argument_nodes

        self.pos_start = self.function_node.pos_start

        if len(argument_nodes) > 0:
            self.pos_end = self.argument_nodes[len(argument_nodes) - 1].pos_end
        else:
            self.pos_end = self.function_node.pos_end


class ListNode:
    def __init__(self, element_nodes, pos_start, pos_end):
        self.element_nodes = element_nodes

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'[{", ".join(str(node) for node in self.element_nodes)}]'

class ReturnNode:
    def __init__(self, node_to_return, pos_start, pos_end):
        self.node_to_return = node_to_return
        self.pos_start = pos_start
        self.pos_end = pos_end

class ContinueNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end

class BreakNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end