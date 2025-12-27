import express from "express";
import dotenv from "dotenv";
import { askFalcon } from "./ai.js";
import { executeArtifact } from "./execute.js";

dotenv.config();

const app = express();
app.use(express.json());

app.post("/run", async (req, res) => {
  const { prompt } = req.body;

  if (!prompt) {
    return res.status(400).json({ error: "Missing prompt" });
  }

  try {
    const result = await askFalcon(prompt);

    let execution = null;

    if (result.run === true) {
      execution = await executeArtifact({
        language: result.language,
        filename: result.filename,
        code: result.code,
        run: result.run
      });
    }

    res.json({
      explanation: result.explanation,
      execution
    });

  } catch (err) {
    res.status(500).json({
      error: "Execution failed",
      details: err.error || err.message
    });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🦅 FALCON SERVER running on port ${PORT}`);
});