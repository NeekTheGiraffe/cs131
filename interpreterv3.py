from intbase import InterpreterBase, ErrorType
from brewparse import parse_program
import copy, sys

BINARY_OPERATORS = set(['+', '-', '*', '/', '==', '<', '<=', '>', '>=', '!=', '&&', '||'])
UNARY_OPERATORS = set(['neg', '!'])
OPERATORS = BINARY_OPERATORS | UNARY_OPERATORS
VALID_OPERAND_TYPES = {
    '+': [
        (['int', 'int'], ('bool', 'int')),
        (['string', 'string'], None),
    ],
    '-': [(['int', 'int'], ('bool', 'int'))],
    '*': [(['int', 'int'], ('bool', 'int'))],
    '/': [(['int', 'int'], ('bool', 'int'))],
    '==': [
        (['bool', 'bool'], ('int', 'bool')),
        (['any', 'any'], None),
    ],
    '!=': [(['any', 'any'], None)],
    '<': [(['int', 'int'], None)],
    '<=': [(['int', 'int'], None)],
    '>': [(['int', 'int'], None)],
    '>=': [(['int', 'int'], None)],
    '&&': [(['bool', 'bool'], ('int', 'bool'))],
    '||': [(['bool', 'bool'], ('int', 'bool'))],
    'neg': [(['int'], None)],
    '!': [(['bool'], ('int', 'bool'))],
}
COERCIONS = {
    ('int', 'bool'): lambda x: TypedValue('bool', x.value != 0),
    ('bool', 'int'): lambda x: TypedValue('int', 1 if x.value else 0),
}

class Closure:
    def __init__(self, definition_node, free_vars):
        self.definition = definition_node
        self.free_vars = free_vars

    def __deepcopy__(self, memo):
        # Don't copy the definition node - it will not be mutated,
        # so copying a whole subtree of the AST would be unnecessary
        return Closure(self.definition, copy.deepcopy(self.free_vars, memo))

class TypedValue:
    def __init__(self, type: str, value: int | str | bool | Closure | dict[int, any] | None):
        self.type = type
        self.value = value
    
    def __repr__(self):
        return f"({self.type} {self.value})"

class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.trace_output = trace_output

    def print_if_trace(self, *args, **kwargs):
        if self.trace_output:
            print(*args, **kwargs, file=sys.stderr)

    def run(self, program):
        ast = parse_program(program)
        self.variables: dict[str, list[TypedValue]] = {} # Maps variable names to a list of shadowed scopes
        self.scopes: list[set[str]] = [set()]

        main_func_node = None
        for func_node in ast.dict['functions']:
            name = func_node.dict['name']
            if self.is_variable_defined(name):
                if self.variables[name][-1].type == 'overloaded_func':
                    self.variables[name][-1].value[len(func_node.dict['args'])] = func_node
                else:
                    first_overload_node = self.variables[name][-1].value.definition
                    self.variables[name][-1] = TypedValue('overloaded_func', {
                        len(first_overload_node.dict['args']): first_overload_node,
                        len(func_node.dict['args']): func_node,
                    })
            else:
                self.scopes[-1].add(name)
                self.variables[name] = [TypedValue('func', Closure(func_node, {}))]
            if name == 'main':
                main_func_node = func_node
        
        if main_func_node is None:
            super().error(
                ErrorType.NAME_ERROR,
                "No main() function was found",
            )
        self.run_statements(main_func_node.dict['statements'])

    def run_statements(self, statement_list):
        for statement_node in statement_list:
            return_val = self.run_statement(statement_node)
            if statement_node.elem_type == 'return' or (statement_node.elem_type in ['if', 'while'] and return_val is not None):
                return return_val
        return None

    def run_statement(self, statement_node):
        match statement_node.elem_type:
            case '=':
                self.do_assignment(statement_node)
                return None
            case 'fcall':
                return self.do_func_call(statement_node)
            case 'if':
                return self.do_if_statement(statement_node)
            case 'while':
                return self.do_while_statement(statement_node)
            case 'return':
                if statement_node.dict['expression'] is None:
                    return TypedValue('nil', None)
                return copy.deepcopy(self.evaluate_expression(statement_node.dict['expression']))

    def is_variable_defined(self, varname):
        return varname in self.variables and len(self.variables[varname]) > 0

    def do_assignment(self, statement_node):
        target_var_name = statement_node.dict['name']
        expression_value = self.evaluate_expression(statement_node.dict['expression'])
        if not self.is_variable_defined(target_var_name):
            self.scopes[-1].add(target_var_name)
            self.variables[target_var_name] = [expression_value]
        else:
            self.variables[target_var_name][-1].type = expression_value.type
            self.variables[target_var_name][-1].value = expression_value.value
    
    def do_func_call(self, func_call_node):
        args = list(map(self.evaluate_expression, func_call_node.dict['args']))
        func_name = func_call_node.dict['name']
        match func_call_node.dict['name']:
            case 'print':
                self.run_print(args)
                return TypedValue('nil', None)
            case 'inputi':
                return self.run_inputi(args)
            case 'inputs':
                return self.run_inputs(args)
        if not self.is_variable_defined(func_name):
            super().error(
                ErrorType.NAME_ERROR,
                f"Function {func_name} that takes {len(args)} parameters has not been defined",
            )

        func_object = self.variables[func_name][-1]
        if func_object.type == 'overloaded_func':
            if len(args) not in func_object.value:
                super().error(
                    ErrorType.NAME_ERROR,
                    f"Function {func_name} that takes {len(args)} parameters has not been defined",
                )
            func_decl_node = func_object.value[len(args)]
            free_vars = {}
        elif func_object.type == 'func':
            func_decl_node = func_object.value.definition
            free_vars = func_object.value.free_vars
            if len(args) != len(func_decl_node.dict['args']):
                super().error(
                    ErrorType.TYPE_ERROR,
                    f"Function {func_name} takes {len(func_decl_node.dict['args'])} parameters but {len(args)} were given",
                )
        else:
            super().error(
                ErrorType.TYPE_ERROR,
                f"Trying to call {func_name} as a function, but it is of type {func_object.type}",
            )

        arg_names = [arg_node.dict['name'] for arg_node in func_decl_node.dict['args']]
        arg_types = [arg_node.elem_type for arg_node in func_decl_node.dict['args']]
        for arg_name, value, arg_type in zip(arg_names, args, arg_types):
            value_to_pass = value if arg_type == 'refarg' else copy.deepcopy(value)
            if not self.is_variable_defined(arg_name):
                self.variables[arg_name] = [value_to_pass]
            else:
                self.variables[arg_name].append(value_to_pass)
        
        arg_names_set = set(arg_names)
        unshadowed_free_vars = [(k, v) for k, v in free_vars.items() if k not in arg_names_set]
        for var_name, value in unshadowed_free_vars:
            # The variable is guaranteed to have been defined at some point,
            # so no need to check
            self.variables[var_name].append(value)
        self.scopes.append(arg_names_set | { k for k, _ in unshadowed_free_vars })

        return_val = self.run_statements(func_decl_node.dict['statements'])

        for varname in self.scopes[-1]:
            self.variables[varname].pop()
        self.scopes.pop()
        
        if return_val is None:
            return TypedValue('nil', None)
        return return_val
    
    def do_if_statement(self, if_statement_node):
        condition = self.try_coerce_to_bool(self.evaluate_expression(if_statement_node.dict['condition']))
        if condition.type != 'bool':
            super().error(
                ErrorType.TYPE_ERROR,
                f"Expected bool inside 'if' condition but got {condition}"
            )
        statements = if_statement_node.dict['statements'] if condition.value else if_statement_node.dict['else_statements']
        if statements is None:
            return None
        self.scopes.append(set())
        return_val = self.run_statements(statements)
        for var_name in self.scopes[-1]:
            self.variables[var_name].pop()
        self.scopes.pop()
        return return_val

    def do_while_statement(self, while_statement_node):
        self.scopes.append(set())

        return_val = None
        while True:
            condition = self.try_coerce_to_bool(self.evaluate_expression(while_statement_node.dict['condition']))
            if condition.type != 'bool':
                super().error(
                    ErrorType.TYPE_ERROR,
                    f"Expected bool inside 'while' condition but got {condition}"
                )
            if not condition.value:
                break
            return_val = self.run_statements(while_statement_node.dict['statements'])
            if return_val is not None:
                break
        
        for var_name in self.scopes[-1]:
            self.variables[var_name].pop()
        self.scopes.pop()
        return return_val

    def evaluate_expression(self, expression_node) -> TypedValue:
        if expression_node.elem_type in OPERATORS:
            return self.evaluate_operation(expression_node)
        match expression_node.elem_type:
            case 'fcall':
                return self.do_func_call(expression_node)
            case 'var':
                return self.get_variable_value(expression_node)
            case 'lambda':
                return self.evaluate_lambda(expression_node)
            case 'nil':
                return TypedValue('nil', None)
            case 'int' | 'string' | 'bool':
                return TypedValue(expression_node.elem_type, expression_node.dict['val'])

    def get_variable_value(self, variable_node):
        var_name = variable_node.dict['name']
        if not self.is_variable_defined(var_name):
            super().error(
                ErrorType.NAME_ERROR,
                f"Variable {var_name} has not been defined",
            )
        typed_value = self.variables[var_name][-1]
        if typed_value.type == 'overloaded_func':
            super().error(
                ErrorType.NAME_ERROR,
                f"Function {var_name} has multiple overloaded versions",
            )
        return typed_value
    
    def evaluate_lambda(self, lambda_node):
        free_vars = { var_name: copy.deepcopy(values[-1]) for var_name, values in self.variables.items() if len(values) > 0 }
        return TypedValue('func', Closure(lambda_node, free_vars))

    def check_operands_and_coerce(self, operands, operator):
        for type_rules in VALID_OPERAND_TYPES[operator]:
            types, valid_coercion = type_rules
            match = True
            coerced = []
            for operand, expected_type in zip(operands, types):
                if expected_type == 'any' or operand.type == expected_type:
                    coerced.append(operand)
                    continue
                if valid_coercion == (operand.type, expected_type):
                    coerced.append(COERCIONS[(operand.type, expected_type)](operand))
                    continue
                match = False
                break
            if match:
                return True, coerced
        return False, None

    def evaluate_operation(self, expression_node) -> TypedValue:
        operator = expression_node.elem_type
        op1 = self.evaluate_expression(expression_node.dict['op1'])
        if operator in BINARY_OPERATORS:
            op2 = self.evaluate_expression(expression_node.dict['op2'])
            operands = [op1, op2]
        else:
            operands = [op1]

        valid_operands, coerced = self.check_operands_and_coerce(operands, operator)
        if not valid_operands:
            super().error(
                ErrorType.TYPE_ERROR,
                f"Incompatible types {', '.join([op.type for op in operands])} for operation {operator}"
            )
        
        op1 = coerced[0]
        if operator in BINARY_OPERATORS:
            op2 = coerced[1]
        
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

    def try_coerce_to_bool(self, integer_or_bool: TypedValue):
        if integer_or_bool.type == 'int':
            return COERCIONS[('int', 'bool')](integer_or_bool)
        return integer_or_bool

    def run_print(self, args):
        output_strs = []
        for x in args:
            if x.type == 'bool':
                output_strs.append("true" if x.value else "false")
            elif x.type == 'nil':
                output_strs.append("nil")
            else:
                output_strs.append(str(x.value))
        super().output("".join(output_strs))

    def run_inputi(self, args):
        if len(args) > 1:
            super().error(
                ErrorType.NAME_ERROR,
                "No inputi() function found that takes >1 parameter",
            )
        if len(args) > 0:
            super().output(args[0].value)
        return TypedValue('int', int(super().get_input()))

    def run_inputs(self, args):
        if len(args) > 1:
            super().error(
                ErrorType.NAME_ERROR,
                "No inputs() function found that takes >1 parameter",
            )
        if len(args) > 0:
            super().output(args[0].value)
        return TypedValue('string', super().get_input())
