export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const { message } = req.body;

  try {
    const response = await fetch("https://api.nofiltergpt.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer OTI2cW5aVFZTZVNsSXIwMTBTbGpHMXZHWjNZMg"
      },
      body: JSON.stringify({
        model: "gpt-3.5-turbo",
        messages: [{ role: "user", content: message }]
      })
    });

    const data = await response.json();
    const reply = data.choices?.[0]?.message?.content || "⚠️ No response from Falcons";

    res.status(200).json({ reply });
  } catch (err) {
    res.status(500).json({ error: "Server error", details: err.message });
  }
}