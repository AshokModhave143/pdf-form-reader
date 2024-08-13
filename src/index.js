// index.js

const express = require("express");
const { spawn } = require("child_process");

const app = express();
app.use(express.json());

function callPythonScript(inputData) {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn("python3", ["script.py"]);

    pythonProcess.stdin.write(JSON.stringify(inputData));
    pythonProcess.stdin.end();

    let data = "";
    pythonProcess.stdout.on("data", (chunk) => {
      data += chunk.toString();
    });

    pythonProcess.stdout.on("end", () => {
      resolve(JSON.parse(data));
    });

    pythonProcess.stderr.on("data", (data) => {
      reject(data.toString());
    });
  });
}

app.get("/api", (req, res) => {
  return res.status(200).json({ message: "hello" });
});

app.post("/api/run-script", (req, res) => {
  callPythonScript(req.body)
    .then((result) => {
      res.json(result);
    })
    .catch((err) => {
      res.status(500).send(err);
    });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
