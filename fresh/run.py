from fresh.context import Context
from fresh.interpreter import Interpreter
from fresh.lexer import Lexer
from fresh.parser import Parser
from fresh.symboltable import SymbolTable
from fresh.values import Number, BuiltInFunction

global_symbol_table = SymbolTable()
global_symbol_table.set('null', Number.null)
global_symbol_table.set('true', Number.true)
global_symbol_table.set('false', Number.false)

global_symbol_table.set('log', BuiltInFunction.log)
global_symbol_table.set('str_input', BuiltInFunction.str_input)
global_symbol_table.set('num_input', BuiltInFunction.num_input)
global_symbol_table.set('clear', BuiltInFunction.clear)
global_symbol_table.set('is_number', BuiltInFunction.is_number)
global_symbol_table.set('is_digit', BuiltInFunction.is_digit)
global_symbol_table.set('is_string', BuiltInFunction.is_string)
global_symbol_table.set('is_list', BuiltInFunction.is_list)
global_symbol_table.set('is_function', BuiltInFunction.is_function)
global_symbol_table.set('append', BuiltInFunction.append)
global_symbol_table.set('pop', BuiltInFunction.pop)
global_symbol_table.set('len', BuiltInFunction.len)
global_symbol_table.set('extend', BuiltInFunction.extend)
global_symbol_table.set('random_int', BuiltInFunction.random_int)
global_symbol_table.set('str', BuiltInFunction.str)
global_symbol_table.set('int', BuiltInFunction.int)
global_symbol_table.set('float', BuiltInFunction.float)
global_symbol_table.set('wait', BuiltInFunction.wait)

def run(filename, text, debug=False):
    lexer = Lexer(filename, text, debug)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error

    # Generate Abstract Syntax Tree

    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error:
        return None, ast.error

    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)

    return result.value, result.error
