import { OpenRouter } from "@openrouter/sdk";
import { SYSTEM_PROMPT } from "./prompt.js";

const openrouter = new OpenRouter({
  apiKey: process.env.OPENROUTER_API_KEY
});

export async function repairOutput(userPrompt, errorMessage, badOutput) {
  const completion = await openrouter.chat.send({
    model: "google/gemini-2.0-flash-exp:free",
    messages: [
      { role: "system", content: SYSTEM_PROMPT },
      {
        role: "user",
        content: `
The previous output was INVALID.

Error:
${errorMessage}

Invalid Output:
${JSON.stringify(badOutput)}

Fix the response so it EXACTLY matches the schema.
Return ONLY valid JSON.
`
      }
    ]
  });

  return JSON.parse(completion.choices[0].message.content);
}