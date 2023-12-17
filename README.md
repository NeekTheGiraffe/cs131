# CS 131 - Brewin' Interpreter

This is my quarter-long project for [CS 131](https://ucla-cs-131.github.io/fall-23-website/)
at UCLA: an interpreter for a custom programming language, Brewin'. The
interpreter is implemented in Python.

In addition to the interpreter, this repository contains a React application
(`frontend/`) and Flask server (`server.py`) for running Brewin' code over the
web, [available here](https://nicks-brewin.fly.dev).

## Key features

- Several data types: integer, string, bool (v2+), nil (v2+), function/lambda
  (v3+), object (v4)
- `if` and `while` statements (v2+)
- Dynamic typing
- Dynamic scoping (v2+)
- First-class function support (v3+)
- Pass-by-value (v2+) and pass-by-reference (v3+) parameter semantics
- Limited type coercions (v3+)
- Objects with prototypal inheritance (v4)

## Usage

### Quick start

The interpreter was tested using Python 3.11.

1. Clone the repository:

```
git clone https://github.com/NeekTheGiraffe/cs131.git
cd cs131
```

2. Create a `main.brewin` file in the project root directory. Here is an example:

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

### Testing

1. (One-time) Ensure the autograder submodule is present:

```
git submodule init
git submodule update
```

2. From the project root directory:

```
python3 test.py [version]
```

## Brewin' web app

### Development setup

Requires Node. The app was tested with Node v18.17.1.

1. (One-time) Set up the server by installing Python dependencies:

```
python3 -m venv .venv
.venv/bin/activate                    # .venv/Scripts/activate on Windows
pip install -r requirements.txt
```

2. (One-time) Set up the frontend by installing Node dependencies:

```
cd frontend
npm install
cd ..
```

3. Start running the server:

```
flask --app server run --debug --port=8000
```

4. In a separate terminal, run the frontend:

```
cd frontend
npm run dev
```

The frontend will be available at http://localhost:5173.

### Testing with Docker

The final Docker container hosts the frontend pages in addition to the Brewin'
"runner" API. To test the final Docker container:

1. Create a Docker image:

```
docker build -t brewin .
```

2. Run a container using the image:

```
docker run -dp 127.0.0.1:8000:8000 brewin
```

3. Stop the container when done:

```
docker stop [CONTAINER NAME]
```

## Licensing and attribution

I am responsible for writing:
- The interpreters: `interpreter*.py`
- The main/test entry points for this repo: `main.py`, `test.py`
- The Flask server: `server.py`
- The frontend app: `frontend/`
- Deployment config: `.github/workflows`, `Dockerfile`, `fly.toml`

For the client-server component, I was heavily inspired by
[Barista](https://barista-f23.fly.dev), the web interface to the course's
canonically-correct interpreter. I am using the same high-level tech stack as
Barista (React and Flask), but the implementation and deployment pipeline are
completely my own.

The other Python files were primarily written by [Carey Nachenberg](http://careynachenberg.weebly.com/),
with support from his TAs for the [Fall 2023 iteration of CS 131](https://ucla-cs-131.github.io/fall-23-website/).
