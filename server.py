from flask import Flask, request, send_from_directory
from flask_cors import CORS
from interpreterv4 import Interpreter as InterpreterV4
from interpreterv3 import Interpreter as InterpreterV3
from interpreterv2 import Interpreter as InterpreterV2
from interpreterv1 import Interpreter as InterpreterV1
import asyncio
from os import environ

TIMEOUT = 5

app = Flask(__name__)

env = environ.get("FLASK_ENV")
origins = ["http://localhost:5173"] if env != "production" else None
# if env != "production":
#     origins = ["http://localhost:5173"]
# else:
#     origins = None
cors = CORS(app, origins=origins)

@app.route("/")
@app.route("/<path:name>")
def get_static_file(name="index.html"):
    return send_from_directory("frontend/", name)

@app.post("/api/run")
async def interpret_program():
    inp = request.json["stdin"].split("\n")

    kwargs = { "console_output": False, "inp": inp, "trace_output": False }

    match request.json["version"]:
        case 4:
            interpreter = InterpreterV4(**kwargs)
        case 3:
            interpreter = InterpreterV3(**kwargs)
        case 2:
            interpreter = InterpreterV2(**kwargs)
        case 1:
            interpreter = InterpreterV1(**kwargs)
        case _:
            raise Exception(f"Unknown version {request.json['version']}")
    
    return await run_program_with_timeout(interpreter, request.json["program"])

def run_program(interpreter, program):
    try:
        interpreter.run(program)
    except SyntaxError:
        return { "stdout": "SyntaxError" }
    except Exception as e:
        error_msg = str(e)
        return { "stdout": error_msg if "ErrorType." in error_msg else "RuntimeError" }
    return { "stdout": "\n".join(interpreter.get_output()) }

async def run_program_with_timeout(interpreter, program):
    try:
        async with asyncio.timeout(TIMEOUT):
            return await asyncio.to_thread(run_program, interpreter, program)
    except asyncio.TimeoutError:
        return { "stdout": "Timeout" }
    
