import { OpenRouter } from "@openrouter/sdk";
import { SYSTEM_PROMPT } from "./prompt.js";
import { validateFalconOutput } from "./validate.js";
import { repairOutput } from "./repair.js";

const openrouter = new OpenRouter({
  apiKey: process.env.OPENROUTER_API_KEY
});

export async function askFalcon(userPrompt) {
  const completion = await openrouter.chat.send({
    model: "google/gemini-2.0-flash-exp:free",
    messages: [
      { role: "system", content: SYSTEM_PROMPT },
      { role: "user", content: userPrompt }
    ]
  });

  let output = JSON.parse(completion.choices[0].message.content);

  const error = validateFalconOutput(output);

  if (!error) {
    return output;
  }

  // 🔁 Self-heal once
  const repaired = await repairOutput(userPrompt, error, output);

  const repairedError = validateFalconOutput(repaired);

  if (repairedError) {
    throw new Error("AI failed validation after repair");
  }

  return repaired;
}