export const examples = {
  "hello-world": {
    "program": "func main() {\n  a = inputi();\n  print(\"Hello \", a);\n}",
    "stdin": "1234",
  },
};

export const apiUrl =
  import.meta.env.PROD ? "/api/run" : "http://127.0.0.1:8000/api/run";
