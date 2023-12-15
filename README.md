# CS 131 - Brewin' Interpreter

This is my quarter-long project for [CS 131](https://ucla-cs-131.github.io/fall-23-website/)
at UCLA: an interpreter for a custom programming language, Brewin'. The
interpreter is implemented in Python.

In addition to the interpreter, this repository contains a React application
(`frontend/`) and Flask server (`server.py`) for running Brewin' code over the
web.

## Key features

- Several data types: integer, string, bool (v2+), nil (v2+), function/lambda
  (v3+), object (v4)
- `if` and `while` statements (v2+)
- Dynamic typing
- Dynamic scoping (v2+)
- First-class function support (v3+)
- Pass-by-value (v2+) and pass-by-reference (v3+) parameter semantics
- Limited type coercions (v3+)
- Objects with prototypal inheritance (v4+)

## Running locally

### Quick start

1. Clone the repository:

```
git clone --recurse-submodules https://github.com/NeekTheGiraffe/cs131.git
cd cs131
```

2. Create a `main.brewin` file. Here is an example:

```
/* main.brewin */

func main() {
    a = 1;
    while (a < 10) {
        print("Hello ", a);
        a = a + 1;
    }
}
```

3. Run the interpreter:

```
python3 main.py
```

### CLI

```
❯ python3 main.py --help
usage: Brewin' Interpreter [-h] [-i INTERPRETER] [filename]

Run a Brewin' program

positional arguments:
  filename              the Brewin' source file

options:
  -h, --help            show this help message and exit
  -i INTERPRETER, --interpreter INTERPRETER
                        interpreter version to use from 1-4
```

## Testing

1. Ensure the autograder submodule is present:

```
git submodule init
git submodule update
```

2. From the project root directory:

```
python test.py [version]
```

## Licensing and Attribution

I am responsible for writing:
- The interpreters: `interpreter*.py`
- The main/test entry points for this repo: `main.py`, `test.py`
- The Flask server: `server.py`
- The frontend app: `frontend/`

For the client-server component, I was heavily inspired by
[Barista](https://barista-f23.fly.dev), the web interface to the course's
canonically-correct interpreter. I am using the same high-level tech stack as
Barista (React and Flask), but the implementation is completely my own.

The other Python files were primarily written by [Carey Nachenberg](http://careynachenberg.weebly.com/),
with support from his TAs for the [Fall 2023 iteration of CS 131](https://ucla-cs-131.github.io/fall-23-website/).
