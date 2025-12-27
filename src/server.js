import express from "express";
import dotenv from "dotenv";
import { askFalcon } from "./ai.js";

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

    res.json({
      message: result.explanation,
      artifact: {
        language: result.language,
        filename: result.filename,
        run: result.run,
        code: result.code
      }
    });

  } catch (err) {
    res.status(500).json({
      error: "AI processing failed",
      details: err.message
    });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🦅 FALCON SERVER running on port ${PORT}`);
});