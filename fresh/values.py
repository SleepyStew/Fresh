import os
import random

from fresh.context import Context
from fresh.errors import RTError as RTError
from fresh.runtimeresult import RuntimeResult
from fresh.symboltable import SymbolTable


class Value:
    def __init__(self):
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def illegal_operation(self, other=None):
        if not other: other = self
        return RTError(
            self.pos_start, other.pos_end,
            'Illegal operation',
            self.context
        )

    def added_to(self, other):
        return None, self.illegal_operation(other)

    def subtracted_by(self, other):
        return None, self.illegal_operation(other)

    def multiplied_by(self, other):
        return None, self.illegal_operation(other)

    def divided_by(self, other):
        return None, self.illegal_operation(other)

    def powered_by(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_equals(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_lessthan(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_greaterthan(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_notequals(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_lessequals(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_greaterequals(self, other):
        return None, self.illegal_operation(other)

    def anded_by(self, other):
        return None, self.illegal_operation(other)

    def ored_by(self, other):
        return None, self.illegal_operation(other)

    def notted(self):
        return None, self.illegal_operation()

    def is_true(self):
        return None, self.illegal_operation()

    def query_by(self, other):
        return None, self.illegal_operation(other)


class Number(Value):
    null = None
    true = True
    false = False

    def __init__(self, value):
        super().__init__()
        self.value = value

    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def subtracted_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def multiplied_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def divided_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    self.pos_start, self.pos_end,
                    'Division by zero',
                    self.context
                )
            return Number(self.value / other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def powered_by(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def get_comparison_equals(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else:
            return Number.false, None

    def get_comparison_lessthan(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def get_comparison_greaterthan(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def get_comparison_notequals(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(self.context), None
        else:
            return Number.true, None

    def get_comparison_lessequals(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def get_comparison_greaterequals(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def anded_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def ored_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def notted(self):
        return Number(int(not self.value)).set_context(self.context), None

    def is_true(self):
        return self.value != 0

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        return str(self.value)


Number.null = Number(0)
Number.false = Number(0)
Number.true = Number(1)


class String(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def added_to(self, other):
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    # Remove specific part of string
    def subtracted_by(self, other):
        if isinstance(other, String):
            return String(str(self.value).replace(other.value, "")).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multiplied_by(self, other):
        if isinstance(other, Number):
            return String(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_equals(self, other):
        if isinstance(other, String):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else:
            return Number.false, None

    def get_comparison_notequals(self, other):
        if isinstance(other, String):
            return Number(int(self.value != other.value)).set_context(self.context), None
        else:
            return Number.true, None

    def anded_by(self, other):
        if isinstance(other, String):
            return Number(int(self.value and other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def ored_by(self, other):
        if isinstance(other, String):
            return Number(int(self.value or other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(other)

    def is_true(self):
        return len(self.value) > 0

    def copy(self):
        copy = String(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        return f'{self.value}'


class BaseFunction(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name or "<anonymous>"

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context

    def check_args(self, arg_names, args):
        response = RuntimeResult()
        args_len = len(args)
        if args_len > len(arg_names):
            return response.failure(RTError(
                self.pos_start, self.pos_end,
                f"{self.name} expected at most {len(arg_names)} arguments, got {args_len}",
                self.context
            ))
        if args_len < len(arg_names):
            return response.failure(RTError(
                self.pos_start, self.pos_end,
                f"{self.name} expected at least {len(arg_names)} arguments, got {args_len}",
                self.context
            ))
        return response.success(None)

    def populate_args(self, arg_names, args, context):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            context.symbol_table.set(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, execute_context):
        response = RuntimeResult()
        response.register(self.check_args(arg_names, args))
        if response.should_return():
            return response
        self.populate_args(arg_names, args, execute_context)
        return response.success(None)

    def __repr__(self):
        return f"<function {self.name}>"


class Function(BaseFunction):
    def __init__(self, name, body_node, arguments, should_auto_return):
        super().__init__(name)
        self.body_node = body_node
        self.arguments = arguments
        self.should_auto_return = should_auto_return

    def execute(self, args):
        response = RuntimeResult()
        from fresh.interpreter import Interpreter
        interpreter = Interpreter()
        execute_context = self.generate_new_context()

        response.register(self.check_and_populate_args(self.arguments, args, execute_context))

        value = response.register(interpreter.visit(self.body_node, execute_context))
        if response.should_return() and response.function_return_value is None:
            return response

        return_value = (value if self.should_auto_return else None) or response.function_return_value or Number.null

        return response.success(return_value)

    def copy(self):
        copy = Function(self.name, self.body_node, self.arguments, self.should_auto_return)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy


class BuiltInFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)

    def execute(self, args):
        response = RuntimeResult()
        execute_context = self.generate_new_context()

        method_name = f"execute_{self.name}"
        method = getattr(self, method_name, self.no_visit_method)
        response.register(self.check_and_populate_args(method.arg_names, args, execute_context))
        if response.should_return():
            return response

        return_value = response.register(method(execute_context))
        if response.should_return():
            return response
        return response.success(return_value)

    def copy(self):
        copy = BuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def execute_log(self, execute_context):
        print(str(execute_context.symbol_table.get('value')))
        return RuntimeResult().success(Number.null)

    execute_log.arg_names = ["value"]

    def execute_str_input(self, execute_context):
        text = input(execute_context.symbol_table.get('prompt'))
        return RuntimeResult().success(String(text))

    execute_str_input.arg_names = ["prompt"]

    def execute_num_input(self, execute_context):
        text = input(execute_context.symbol_table.get('prompt'))
        try:
            number = int(text)
        except ValueError:
            return RuntimeResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Expected number input",
                self.context
            ))
        return RuntimeResult().success(Number(number))

    execute_num_input.arg_names = ["prompt"]

    def execute_clear(self, execute_context):
        os.system('cls' if os.name == 'nt' else 'clear')
        return RuntimeResult().success(Number.null)

    execute_clear.arg_names = []

    def execute_is_number(self, execute_context):
        is_number = isinstance(execute_context.symbol_table.get('value'), Number)
        return RuntimeResult().success(Number.true if is_number else Number.false)

    execute_is_number.arg_names = ['value']

    def execute_is_string(self, execute_context):
        is_number = isinstance(execute_context.symbol_table.get('value'), String)
        return RuntimeResult().success(Number.true if is_number else Number.false)

    execute_is_string.arg_names = ['value']

    def execute_is_list(self, execute_context):
        is_number = isinstance(execute_context.symbol_table.get('value'), List)
        return RuntimeResult().success(Number.true if is_number else Number.false)

    execute_is_list.arg_names = ['value']

    def execute_is_function(self, execute_context):
        is_number = isinstance(execute_context.symbol_table.get('value'), BaseFunction)
        return RuntimeResult().success(Number.true if is_number else Number.false)

    execute_is_function.arg_names = ['value']

    def execute_append(self, execute_context):
        list_ = execute_context.symbol_table.get('list')
        value = execute_context.symbol_table.get('value')

        if not isinstance(list_, List):
            return RuntimeResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be a list",
                self.context
            ))
        list_.elements.append(value)
        return RuntimeResult().success(list_)

    execute_append.arg_names = ['list', 'value']

    def execute_pop(self, execute_context):
        list_ = execute_context.symbol_table.get('list')
        index = execute_context.symbol_table.get('index')

        if not isinstance(list_, List):
            return RuntimeResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be a list",
                self.context
            ))
        if not isinstance(index, Number):
            return RuntimeResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Second argument must be a number",
                self.context
            ))
        try:
            value = list_.elements.pop(index.value)
        except IndexError:
            return RuntimeResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Index out of bounds",
                self.context
            ))
        return RuntimeResult().success(value)

    execute_pop.arg_names = ['list', 'index']

    def execute_len(self, execute_context):
        list_ = execute_context.symbol_table.get('value')

        if isinstance(list_, String):
            return RuntimeResult().success(Number(len(list_.value)))
        elif isinstance(list_, List):
            return RuntimeResult().success(Number(len(list_.elements)))
        else:
            return RuntimeResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Argument must be type list or string",
                self.context
            ))

    execute_len.arg_names = ['value']

    def execute_extend(self, execute_context):
        list1_ = execute_context.symbol_table.get('list1')
        list2_ = execute_context.symbol_table.get('list2')

        if not isinstance(list1_, List):
            return RuntimeResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be a list",
                self.context
            ))
        if not isinstance(list2_, List):
            return RuntimeResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Second argument must be a list",
                self.context
            ))
        list1_.elements.extend(list2_.elements)
        return RuntimeResult().success(list1_)

    execute_extend.arg_names = ['list1', 'list2']

    def execute_random_int(self, execute_context):
        min_ = execute_context.symbol_table.get('min')
        max_ = execute_context.symbol_table.get('max')

        if not isinstance(min_, Number):
            return RuntimeResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be a number",
                self.context
            ))
        if not isinstance(max_, Number):
            return RuntimeResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Second argument must be a number",
                self.context
            ))
        return RuntimeResult().success(Number(random.randint(min_.value, max_.value)))

    execute_random_int.arg_names = ['min', 'max']

    def execute_str(self, execute_context):
        value = execute_context.symbol_table.get('value')
        if not isinstance(value, Number):
            return RuntimeResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Argument must be a number",
                self.context
            ))
        return RuntimeResult().success(String(str(value.value)))

    execute_str.arg_names = ['value']

    def execute_int(self, execute_context):
        value = execute_context.symbol_table.get('value')
        if not isinstance(value, String):
            return RuntimeResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Argument must be a string",
                self.context
            ))
        try:
            return RuntimeResult().success(Number(int(value.value)))
        except ValueError:
            return RuntimeResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Could not convert string to int",
                self.context
            ))

    execute_int.arg_names = ['value']

    def execute_float(self, execute_context):
        value = execute_context.symbol_table.get('value')
        if not isinstance(value, String):
            return RuntimeResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Argument must be a string",
                self.context
            ))
        try:
            return RuntimeResult().success(Number(float(value.value)))
        except ValueError:
            return RuntimeResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Could not convert string to float",
                self.context
            ))

    execute_float.arg_names = ['value']

    def execute_is_digit(self, execute_context):
        value = execute_context.symbol_table.get('value')
        if not isinstance(value, String):
            return RuntimeResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Argument must be a string",
                self.context
            ))
        return RuntimeResult().success(Number.true if value.value.isdigit() else Number.false)

    execute_is_digit.arg_names = ['value']


    def no_visit_method(self, node, context):
        raise Exception(f"No execute_{self.name} method defined")

    def __repr__(self):
        return f"<builtinfunction {self.name}>"


BuiltInFunction.log = BuiltInFunction("log")
BuiltInFunction.str_input = BuiltInFunction("str_input")
BuiltInFunction.num_input = BuiltInFunction("num_input")
BuiltInFunction.clear = BuiltInFunction("clear")
BuiltInFunction.is_number = BuiltInFunction("is_number")
BuiltInFunction.is_string = BuiltInFunction("is_string")
BuiltInFunction.is_list = BuiltInFunction("is_list")
BuiltInFunction.is_function = BuiltInFunction("is_function")
BuiltInFunction.append = BuiltInFunction("append")
BuiltInFunction.pop = BuiltInFunction("pop")
BuiltInFunction.len = BuiltInFunction("len")
BuiltInFunction.extend = BuiltInFunction("extend")
BuiltInFunction.random_int = BuiltInFunction("random_int")
BuiltInFunction.str = BuiltInFunction("str")
BuiltInFunction.int = BuiltInFunction("int")
BuiltInFunction.float = BuiltInFunction("float")
BuiltInFunction.is_digit = BuiltInFunction("is_digit")

class List(Value):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements

    def added_to(self, other):
        new_list = self.copy_as_true_new()
        new_list.elements.append(other)
        return new_list, None

    def copy(self):
        copy = List(self.elements)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def copy_as_true_new(self):
        copy = List(self.elements[:])
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def multiplied_by(self, other):
        if isinstance(other, List):
            new_list = self.copy_as_true_new()
            new_list.elements.extend(other.elements)
            return new_list, None
        else:
            return None, Value.illegal_operation(self, other)

    def subtracted_by(self, other):
        if isinstance(other, Number):
            new_list = self.copy_as_true_new()
            try:
                new_list.elements.pop(other.value)
                return new_list, None
            except IndexError:
                return None, RTError(
                    self.pos_start, self.pos_end,
                    f"Index out of bounds",
                    self.context
                )
        else:
            return None, Value.illegal_operation(self, other)

    def query_by(self, other):
        if isinstance(other, Number):
            try:
                return self.elements[other.value], None
            except IndexError:
                return None, RTError(
                    self.pos_start, self.pos_end,
                    f"Index out of bounds",
                    self.context
                )
        else:
            return None, Value.illegal_operation(self, other)

    def __repr__(self):
        return f"{self.elements}"
