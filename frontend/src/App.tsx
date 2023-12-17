import { useState } from 'react'
import Editor from 'react-simple-code-editor'
import Prism from 'prismjs';
import './App.css'
import { examples, apiUrl } from './constants';

function App() {
  const [program, setProgram] = useState(examples['hello-world'].program);
  const [stdin, setStdin] = useState(examples['hello-world'].stdin);
  const [result, setResult] = useState("");
  const [version, setVersion] = useState("4");

  return (
    <>
      <h1 className="heading">Brewin' Interpreter</h1>
      <h2 className="subheading">Brewin' is a dynamically-typed, dynamically-scoped programming language.</h2>

      <h3>Program code</h3>
      <Editor
        value={program}
        onValueChange={code => setProgram(code)}
        padding={8}
        highlight={code => Prism.highlight(code, {}, "brewin")}
        className='code-block program'
        style={{
          fontFamily: '"Fira Code", "Fira Mono", monospace',
        }}
      />
      <h3>Input</h3>
      <Editor
        value={stdin}
        onValueChange={code => setStdin(code)}
        padding={8}
        highlight={code => Prism.highlight(code, {}, "none")}
        className='code-block'
        style={{
          fontFamily: '"Fira Code", "Fira Mono", monospace',
        }}
        />
      <div className='control-panel'>
        <h3>Output</h3>
        <select
          value={version}
          onChange={e => { console.log(e.target.value); setVersion(e.target.value)}}
        >
          <option value={"4"}>v4: Brewin#</option>
          <option value={"3"}>v3: Brewin++</option>
          <option value={"2"}>v2: Brewin+</option>
          <option value={"1"}>v1: Brewin</option>
        </select>
        <button
          className='run-button'
          onClick={async () => {
            try {
              const response = await fetch(apiUrl,
              {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                },
                body: JSON.stringify({
                  program,
                  stdin,
                  version: Number(version),
                }),
              });
              const json = await response.json();
              console.log("json", json);
              setResult(json.stdout);
            } catch (e) {
              setResult("Connection error");
            }
          }}
        >
          Run
        </button>
      </div>
      <textarea disabled={true} value={result} className='code-block output'></textarea>
      <h2>About</h2>
      <p>
        Brewin' is a custom programming language made for UCLA's CS 131 class. I made my own
        web interface to demonstrate my project implementation, which is in Python.
      </p>
      <p>
        Check out
        the <a href="https://github.com/NeekTheGiraffe/cs131/" target='_blank'>project source code</a> on GitHub,
        or the <a href="https://ucla-cs-131.github.io/fall-23-website/projects/" target='_blank'>full language specifications</a>.
      </p>
    </>
  )
}

export default App
