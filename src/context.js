export function buildContext(session) {
  if (!session.history.length) return "";

  return `
Previous interactions:
${session.history
  .map((h, i) => `${i + 1}. User: ${h.user}\n   FALCON: ${h.summary}`)
  .join("\n")}
`;
}