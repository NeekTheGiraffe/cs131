from intbase import InterpreterBase, ErrorType
from brewparse import parse_program

BINARY_OPERATORS = set(['+', '-', '*', '/', '==', '<', '<=', '>', '>=', '!=', '&&', '||'])
UNARY_OPERATORS = set(['neg', '!'])
OPERATORS = BINARY_OPERATORS | UNARY_OPERATORS
VALID_OPERAND_TYPES = {
    '+': [['int', 'int'], ['string', 'string']],
    '-': [['int', 'int']],
    '*': [['int', 'int']],
    '/': [['int', 'int']],
    '==': [['any', 'any']],
    '<': [['int', 'int']],
    '<=': [['int', 'int']],
    '>': [['int', 'int']],
    '>=': [['int', 'int']],
    '!=': [['any', 'any']],
    '&&': [['bool', 'bool']],
    '||': [['bool', 'bool']],
    'neg': [['int']],
    '!': [['bool']],
}

class TypedValue:
    def __init__(self, type: str, value: int | str | bool | None):
        self.type = type
        self.value = value

class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)

    def run(self, program):
        ast = parse_program(program)
        self.variable_name_to_value: dict[str, TypedValue] = {}

        main_func_node = next((func for func in ast.dict['functions'] if func.dict['name'] == 'main'), None)
        if main_func_node is None:
            super().error(
                ErrorType.NAME_ERROR,
                "No main() function was found",
            )
        self.run_func(main_func_node)

    def run_func(self, func_node):
        for statement_node in func_node.dict['statements']:
            self.run_statement(statement_node)

    def run_statement(self, statement_node):
        match statement_node.elem_type:
            case '=':
                self.do_assignment(statement_node)
            case 'fcall':
                self.do_func_call(statement_node)

    def do_assignment(self, statement_node):
        target_var_name = statement_node.dict['name']
        expression_value = self.evaluate_expression(statement_node.dict['expression'])
        self.variable_name_to_value[target_var_name] = expression_value
    
    def do_func_call(self, func_node):
        args = list(map(self.evaluate_expression, func_node.dict['args']))
        match func_node.dict['name']:
            case 'print':
                self.run_print(args)
            case 'inputi':
                return self.run_inputi(args)
            case unknown_func_name:
                super().error(
                    ErrorType.NAME_ERROR,
                    f"Function {unknown_func_name} has not been defined",
                )
     
    def evaluate_expression(self, expression_node) -> TypedValue:
        if expression_node.elem_type in OPERATORS:
            return self.evaluate_operation(expression_node)
        match expression_node.elem_type:
            case 'fcall':
                return self.do_func_call(expression_node)
            case 'var':
                return self.get_variable_value(expression_node)
            case 'nil':
                return TypedValue('nil', None)
            case 'int' | 'string' | 'bool':
                return TypedValue(expression_node.elem_type, expression_node.dict['val'])

    def get_variable_value(self, variable_node):
        var_name = variable_node.dict['name']
        if not var_name in self.variable_name_to_value:
            super().error(
                ErrorType.NAME_ERROR,
                f"Variable {var_name} has not been defined",
            )
        return self.variable_name_to_value[var_name]

    def do_operand_types_match(self, operands, operator):
        for types in VALID_OPERAND_TYPES[operator]:
            match = True
            for operand, type in zip(operands, types):
                if type != 'any' and operand.type != type:
                    match = False
                    break
            if match:
                return True
        return False

    def evaluate_operation(self, expression_node) -> TypedValue:
        operator = expression_node.elem_type
        op1 = self.evaluate_expression(expression_node.dict['op1'])
        if operator in BINARY_OPERATORS:
            op2 = self.evaluate_expression(expression_node.dict['op2'])
            operands = [op1, op2]
        else:
            operands = [op1]

        if not self.do_operand_types_match(operands, operator):
            super().error(
                ErrorType.TYPE_ERROR,
                f"Incompatible types {', '.join(operands)} for operation {operator}"
            )
        match operator:
            case '+':
                return TypedValue(op1.type, op1.value + op2.value)
            case '-':
                return TypedValue('int', op1.value - op2.value)
            case '*':
                return TypedValue('int', op1.value * op2.value)
            case '*':
                return TypedValue('int', op1.value * op2.value)
            case '/':
                return TypedValue('int', op1.value // op2.value)
            case '==':
                return TypedValue('bool', op1.type == op2.type and op1.value == op2.value)
            case '!=':
                return TypedValue('bool', op1.type != op2.type or op1.value != op2.value)
            case '<':
                return TypedValue('bool', op1.value < op2.value)
            case '<=':
                return TypedValue('bool', op1.value <= op2.value)
            case '>':
                return TypedValue('bool', op1.value > op2.value)
            case '>=':
                return TypedValue('bool', op1.value >= op2.value)
            case '&&':
                return TypedValue('bool', op1.value and op2.value)
            case '||':
                return TypedValue('bool', op1.value or op2.value)
            case 'neg':
                return TypedValue('int', -op1.value)
            case '!':
                return TypedValue('bool', not op1.value)

    def run_print(self, args):
        string_to_output = "".join([str(x.value) for x in args])
        super().output(string_to_output)

    def run_inputi(self, args):
        if len(args) > 1:
            super().error(
                ErrorType.NAME_ERROR,
                "No inputi() function found that takes >1 parameter",
            )
        if len(args) > 0:
            super().output(args[0].value)
        return TypedValue('int', int(super().get_input()))
