from intbase import InterpreterBase, ErrorType
from brewparse import parse_program

class TypedValue:
    def __init__(self, type: str, value):
        self.type = type
        self.value = value

class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)

    def run(self, program):
        ast = parse_program(program)
        self.variable_name_to_value: dict[str, TypedValue] = {}

        main_func_node = next((func for func in ast.dict['functions'] if func.dict['name'] == 'main'), None)
        if main_func_node == None:
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
        match expression_node.elem_type:
            case '+' | '-':
                return self.evaluate_binary_operator(expression_node)
            case 'fcall':
                return self.do_func_call(expression_node)
            case 'var':
                return self.get_variable_value(expression_node)
            case 'int' | 'string':
                return TypedValue(expression_node.elem_type, expression_node.dict['val'])

    def get_variable_value(self, variable_node):
        var_name = variable_node.dict['name']
        if not var_name in self.variable_name_to_value:
            super().error(
                ErrorType.NAME_ERROR,
                f"Variable {var_name} has not been defined",
            )
        return self.variable_name_to_value[var_name]

    def evaluate_binary_operator(self, expression_node) -> TypedValue:
        op1 = self.evaluate_expression(expression_node.dict['op1'])
        op2 = self.evaluate_expression(expression_node.dict['op2'])
        if op1.type != 'int' or op2.type != 'int':
            super().error(
                ErrorType.TYPE_ERROR,
                f"Incompatible types {op1.type} and {op2.type} for arithmetic operation",
            )
        match expression_node.elem_type:
            case '+':
                return TypedValue('int', op1.value + op2.value)
            case '-':
                return TypedValue('int', op1.value - op2.value)
    
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
        return int(super().get_input())
