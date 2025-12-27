import { OpenRouter } from "@openrouter/sdk";
import { SYSTEM_PROMPT } from "./prompt.js";

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

  const raw = completion.choices[0].message.content;

  // Hard parse (fail fast)
  return JSON.parse(raw);
}