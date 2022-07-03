from fresh.errors import InvalidSyntaxError, ERROR_STRING_2, ERROR_STRING_1
from fresh.tokens import *
from fresh.nodes import NumberNode, BinOpNode, UnaryOpNode, VariableAccessNode, VariableAssignNode, IfNode, ForNode, WhileNode, FunctionDefinitionNode, CallNode, \
    StringNode, ListNode, ReturnNode, ContinueNode, BreakNode
from fresh.parseresult import ParseResult


class Parser:
    def __init__(self, tokens):
        self.current_token = None
        self.tokens = tokens
        self.token_index = -1
        self.advance()

    def advance(self):
        self.token_index += 1
        self.update_current_token()
        return self.current_token

    def reverse(self, amount=1):
        self.token_index -= amount
        self.update_current_token()
        return self.current_token

    def update_current_token(self):
        if 0 <= self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]

    def parse(self):
        res = self.statements()
        if not res.error and self.current_token.type != TT_EOF:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "b5 " + ERROR_STRING_2
            ))
        return res

    def statements(self):
        response = ParseResult()
        statements = []
        pos_start = self.current_token.pos_start.copy()

        while self.current_token.type == TT_NEWLINE:
            response.register_advancement()
            self.advance()

        statement = response.register(self.statement())
        if response.error:
            return response
        statements.append(statement)

        more_statements = True

        while True:
            newline_count = 0
            while self.current_token.type == TT_NEWLINE:
                response.register_advancement()
                self.advance()
                newline_count += 1
            if newline_count == 0:
                more_statements = False

            if not more_statements:
                break

            statement = response.try_register(self.statement())
            if not statement:
                self.reverse(response.to_reverse_count)
                more_statements = False
                continue
            statements.append(statement)

        return response.success(ListNode(statements, pos_start, self.current_token.pos_end.copy()))

    def statement(self):
        response = ParseResult()
        pos_start = self.current_token.pos_start.copy()

        if self.current_token.matches(TT_KEYWORD, 'return'):
            response.register_advancement()
            self.advance()

            expression = response.try_register(self.expression())
            if not expression:
                self.reverse(response.to_reverse_count)
            return response.success(ReturnNode(expression, pos_start, self.current_token.pos_end.copy()))

        if self.current_token.matches(TT_KEYWORD, 'continue'):
            response.register_advancement()
            self.advance()
            return response.success(ContinueNode(pos_start, self.current_token.pos_end.copy()))

        if self.current_token.matches(TT_KEYWORD, 'break'):
            response.register_advancement()
            self.advance()
            return response.success(BreakNode(pos_start, self.current_token.pos_end.copy()))

        expression = response.register(self.expression())

        if response.error:
            return response

        return response.success(expression)

    def if_expression(self):
        response = ParseResult()
        all_cases = response.register(self.if_expression_cases('if'))
        if response.error:
            return response
        cases, else_case = all_cases
        return response.success(IfNode(cases, else_case))

    def if_expression_b(self):
        return self.if_expression_cases('elif')

    def if_expression_c(self):
        response = ParseResult()
        else_case = None

        if self.current_token.matches(TT_KEYWORD, 'else'):
            response.register_advancement()
            self.advance()

            if self.current_token.type == TT_NEWLINE:
                response.register_advancement()
                self.advance()

                statements = response.register(self.statements())
                if response.error:
                    return response
                else_case = (statements, True)

                if self.current_token.matches(TT_KEYWORD, 'end'):
                    response.register_advancement()
                    self.advance()
                else:
                    return response.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "Expected 'end'"
                    ))
            else:
                expression = response.register(self.statement())
                if response.error:
                    return response
                else_case = (expression, False)

        return response.success(else_case)

    def if_expression_b_or_c(self):
        response = ParseResult()
        cases, else_case = [], None

        if self.current_token.matches(TT_KEYWORD, 'elif'):
            all_cases = response.register(self.if_expression_b())
            if response.error:
                return response
            cases, else_case = all_cases
        else:
            else_case = response.register(self.if_expression_c())
            if response.error:
                return response

        return response.success((cases, else_case))

    def if_expression_cases(self, case_keyword):
        response = ParseResult()
        cases = []
        else_case = None

        if not self.current_token.matches(TT_KEYWORD, case_keyword):
            return response.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected 'if'"
            ))

        response.register_advancement()
        self.advance()

        condition = response.register(self.expression())
        if response.error:
            return response

        if not self.current_token.matches(TT_KEYWORD, 'then'):
            return response.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected 'then'"
            ))

        response.register_advancement()
        self.advance()

        if self.current_token.type == TT_NEWLINE:
            response.register_advancement()
            self.advance()

            statements = response.register(self.statements())
            if response.error:
                return response
            cases.append((condition, statements, True))

            if self.current_token.matches(TT_KEYWORD, 'end'):
                response.register_advancement()
                self.advance()
            else:
                all_cases = response.register(self.if_expression_b_or_c())
                if response.error:
                    return response
                new_cases, else_case = all_cases
                cases.extend(new_cases)
        else:
            expression = response.register(self.statement())
            if response.error:
                return response
            cases.append((condition, expression, False))

            all_cases = response.register(self.if_expression_b_or_c())
            if response.error:
                return response
            new_cases, else_case = all_cases
            cases.extend(new_cases)

        return response.success((cases, else_case))

    def for_expression(self):
        response = ParseResult()

        if not self.current_token.matches(TT_KEYWORD, 'for'):
            return response.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected 'for'"
            ))

        response.register_advancement()
        self.advance()

        if self.current_token.type != TT_IDENTIFIER:
            return response.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected IDENTIFIER"
            ))

        variable_name = self.current_token
        response.register_advancement()
        self.advance()

        if self.current_token.type != TT_EQUALS:
            return response.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '='"
            ))

        response.register_advancement()
        self.advance()

        initial_value = response.register(self.expression())
        if response.error:
            return response

        if not self.current_token.matches(TT_KEYWORD, 'to'):
            return response.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected 'to'"
            ))

        response.register_advancement()
        self.advance()

        end_value = response.register(self.expression())
        if response.error:
            return response

        if self.current_token.matches(TT_KEYWORD, 'step'):
            response.register_advancement()
            self.advance()

            step_value = response.register(self.expression())
            if response.error:
                return response
        else:
            step_value = None

        if not self.current_token.matches(TT_KEYWORD, 'then'):
            return response.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected 'then'"
            ))

        response.register_advancement()
        self.advance()

        if self.current_token.type == TT_NEWLINE:
            response.register_advancement()
            self.advance()

            body = response.register(self.statements())
            if response.error:
                return response

            if not self.current_token.matches(TT_KEYWORD, 'end'):
                return response.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected 'end'"
                ))

            response.register_advancement()
            self.advance()

            return response.success(ForNode(variable_name, initial_value, end_value, step_value, body, True))

        body = response.register(self.statement())
        if response.error:
            return response

        return response.success(ForNode(variable_name, initial_value, end_value, step_value, body, False))

    def while_expression(self):
        response = ParseResult()

        if not self.current_token.matches(TT_KEYWORD, 'while'):
            return response.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected 'while'"
            ))

        response.register_advancement()
        self.advance()

        condition = response.register(self.expression())
        if response.error:
            return response

        if not self.current_token.matches(TT_KEYWORD, 'then'):
            return response.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected 'then'"
            ))

        response.register_advancement()
        self.advance()

        if self.current_token.type == TT_NEWLINE:
            response.register_advancement()
            self.advance()

            body = response.register(self.statements())
            if response.error:
                return response

            if not self.current_token.matches(TT_KEYWORD, 'end'):
                return response.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected 'end'"
                ))

            response.register_advancement()
            self.advance()

            return response.success(WhileNode(condition, body, True))

        body = response.register(self.statement())
        if response.error:
            return response

        return response.success(WhileNode(condition, body, False))

    def call(self):
        response = ParseResult()
        atom = response.register(self.atom())
        if response.error:
            return response

        if self.current_token.type == TT_LPAREN:
            response.register_advancement()
            self.advance()

            arguments = []
            if self.current_token.type == TT_RPAREN:
                response.register_advancement()
                self.advance()
            else:
                arguments.append(response.register(self.expression()))
                if response.error:
                    return response.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "b6 " + ERROR_STRING_2
                    ))

                while self.current_token.type == TT_COMMA:
                    response.register_advancement()
                    self.advance()

                    arguments.append(response.register(self.expression()))
                    if response.error:
                        return response

                if self.current_token.type != TT_RPAREN:
                    return response.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "Expected ',' or ')'"
                    ))

                response.register_advancement()
                self.advance()
            return response.success(CallNode(atom, arguments))
        return response.success(atom)

    def atom(self):
        response = ParseResult()
        token = self.current_token

        if token.type in (TT_INT, TT_FLOAT):
            response.register_advancement()
            self.advance()
            return response.success(NumberNode(token))

        if token.type == TT_STRING:
            response.register_advancement()
            self.advance()
            return response.success(StringNode(token))

        elif token.type == TT_IDENTIFIER:
            response.register_advancement()
            self.advance()
            return response.success(VariableAccessNode(token))

        elif token.type == TT_LPAREN:
            response.register_advancement()
            self.advance()
            expression = response.register(self.expression())
            if response.error:
                return response
            if self.current_token.type == TT_RPAREN:
                response.register_advancement()
                self.advance()
                return response.success(expression)
            else:
                return response.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected ')'"
                ))
        elif token.matches(TT_KEYWORD, 'if'):
            if_expression = response.register(self.if_expression())
            if response.error:
                return response
            return response.success(if_expression)

        elif token.matches(TT_KEYWORD, 'for'):
            for_expression = response.register(self.for_expression())
            if response.error:
                return response
            return response.success(for_expression)

        elif token.matches(TT_KEYWORD, 'while'):
            while_expression = response.register(self.while_expression())
            if response.error:
                return response
            return response.success(while_expression)

        elif token.matches(TT_KEYWORD, 'func'):
            function_definition = response.register(self.function_definition())
            if response.error:
                return response
            return response.success(function_definition)

        elif token.type == TT_LSQUAREBRACKET:
            list_expression = response.register(self.list_expression())
            if response.error:
                return response
            return response.success(list_expression)

        return response.failure(InvalidSyntaxError(token.pos_start, token.pos_end, "b3 " + ERROR_STRING_2))

    def power(self):
        return self.binary_operation(self.call, (TT_POW,), self.factor)

    def factor(self):
        response = ParseResult()
        token = self.current_token

        if token.type in (TT_PLUS, TT_MINUS):
            response.register_advancement()
            self.advance()
            factor = response.register(self.factor())
            if response.error:
                return response
            return response.success(UnaryOpNode(token, factor))

        return self.power()

    def term(self):
        return self.binary_operation(self.factor, (TT_MUL, TT_DIV, TT_QUESTIONMARK))

    def arithmatic_expression(self):
        return self.binary_operation(self.term, (TT_PLUS, TT_MINUS))

    def comparison_expression(self):
        response = ParseResult()

        if self.current_token.matches(TT_KEYWORD, 'not'):
            operator_token = self.current_token
            response.register_advancement()
            self.advance()

            node = response.register(self.comparison_expression())
            if response.error:
                return response
            return response.success(UnaryOpNode(operator_token, node))

        node = response.register(
            self.binary_operation(self.arithmatic_expression, (TT_DOUBLEEQUALS, TT_LESS, TT_LESSEQUALS, TT_GREATER, TT_GREATEREQUALS, TT_NOTEQUALS)))

        if response.error:
            return response.failure(
                InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "b4 " + ERROR_STRING_2))

        return response.success(node)

    def expression(self):
        response = ParseResult()

        if self.current_token.matches(TT_KEYWORD, 'set'):
            response.register_advancement()
            self.advance()

            if self.current_token.type != TT_IDENTIFIER:
                return response.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected identifier"
                ))
            identifier = self.current_token
            response.register_advancement()
            self.advance()

            if self.current_token.type != TT_EQUALS:
                return response.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected '='"
                ))

            response.register_advancement()
            self.advance()
            expression = response.register(self.expression())
            if response.error:
                return response
            return response.success(VariableAssignNode(identifier, expression))

        node = response.register(self.binary_operation(self.comparison_expression, ((TT_KEYWORD, "and"), (TT_KEYWORD, "or"))))
        if response.error:
            return response.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                ERROR_STRING_1
            ))

        return response.success(node)

    def binary_operation(self, function_a, operator_tokens, function_b=None):
        if function_b is None:
            function_b = function_a
        response = ParseResult()
        left_factor = response.register(function_a())
        if response.error:
            return response

        while self.current_token.type in operator_tokens or (self.current_token.type, self.current_token.value) in operator_tokens:
            token = self.current_token
            response.register_advancement()
            self.advance()
            right_factor = response.register(function_b())
            if response.error:
                return response
            left_factor = BinOpNode(left_factor, token, right_factor)

        return response.success(left_factor)

    def function_definition(self):
        response = ParseResult()

        if not self.current_token.matches(TT_KEYWORD, 'func'):
            return response.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected 'func'"
            ))

        response.register_advancement()
        self.advance()

        if self.current_token.type == TT_IDENTIFIER:
            variable_name_token = self.current_token
            response.register_advancement()
            self.advance()
            if self.current_token.type != TT_LPAREN:
                return response.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected '('"
                ))
        else:
            variable_name_token = None
            if self.current_token.type != TT_LPAREN:
                return response.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected identifier or '('"
                ))

        response.register_advancement()
        self.advance()
        argument_node_tokens = []

        if self.current_token.type == TT_IDENTIFIER:
            argument_node_tokens.append(self.current_token)
            response.register_advancement()
            self.advance()

            while self.current_token.type == TT_COMMA:
                response.register_advancement()
                self.advance()

                if self.current_token.type != TT_IDENTIFIER:
                    return response.failure(InvalidSyntaxError(
                        self.current_token.pos_start, self.current_token.pos_end,
                        "Expected identifier"
                    ))

                argument_node_tokens.append(self.current_token)
                response.register_advancement()
                self.advance()

            if self.current_token.type != TT_RPAREN:
                return response.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected ',' or ')'"
                ))
        else:
            if self.current_token.type != TT_RPAREN:
                return response.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected identifier or ')'"
                ))

        response.register_advancement()
        self.advance()

        if self.current_token.type == TT_ARROW:

            response.register_advancement()
            self.advance()

            body_node = response.register(self.expression())
            if response.error:
                return response

            return response.success(FunctionDefinitionNode(variable_name_token, argument_node_tokens, body_node, True))

        if self.current_token.type != TT_NEWLINE:
            return response.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '->' or NEWLINE"
            ))

        response.register_advancement()
        self.advance()

        body_node = response.register(self.statements())
        if response.error:
            return response

        if not self.current_token.matches(TT_KEYWORD, 'end'):
            return response.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected 'end'"
            ))

        response.register_advancement()
        self.advance()

        return response.success(FunctionDefinitionNode(variable_name_token, argument_node_tokens, body_node, False))

    def list_expression(self):
        response = ParseResult()
        element_nodes = []
        pos_start = self.current_token.pos_start.copy()

        if self.current_token.type != TT_LSQUAREBRACKET:
            return response.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected '['"
            ))

        response.register_advancement()
        self.advance()

        if self.current_token.type == TT_RSQUAREBRACKET:
            response.register_advancement()
            self.advance()
            return response.success(ListNode(element_nodes, pos_start, self.current_token.pos_end.copy()))
        else:
            element_nodes.append(response.register(self.expression()))
            if response.error:
                return response.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "b7 " + ERROR_STRING_2
                ))

            while self.current_token.type == TT_COMMA:
                response.register_advancement()
                self.advance()

                element_nodes.append(response.register(self.expression()))
                if response.error:
                    return response

            if self.current_token.type != TT_RSQUAREBRACKET:
                return response.failure(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected ',' or ']'"
                ))

            response.register_advancement()
            self.advance()

        return response.success(ListNode(element_nodes, pos_start, self.current_token.pos_end.copy()))
