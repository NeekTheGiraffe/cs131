from interpreterv1 import Interpreter as InterpreterV1
from interpreterv2 import Interpreter as InterpreterV2
from interpreterv3 import Interpreter as InterpreterV3
from interpreterv4 import Interpreter as InterpreterV4
from argparse import ArgumentParser

def main():
    parser = ArgumentParser(prog="Brewin' Interpreter",
                            description="Run a Brewin' program")
    parser.add_argument("filename", nargs='?', default="main.brewin", help="the Brewin' source file")
    parser.add_argument("-i", "--interpreter", type=int, default=4, help="interpreter version to use from 1-4")

    args = parser.parse_args()
    
    interpreter_kwargs = { 'trace_output': True }
    match args.interpreter:
        case 1:
            interpreter = InterpreterV1(**interpreter_kwargs)
        case 2:
            interpreter = InterpreterV2(**interpreter_kwargs)
        case 3:
            interpreter = InterpreterV3(**interpreter_kwargs)
        case 4:
            interpreter = InterpreterV4(**interpreter_kwargs)
        case _:
            print(f"Invalid interpreter version {args.interpreter}. Must be from 1-4")
            exit(1)

    with open(args.filename) as infile:
        program_source = infile.read()

    interpreter.run(program_source)

if __name__ == '__main__':
    main()
