import crypto from "crypto";

const sessions = new Map();

export function getSession(sessionId) {
  if (!sessions.has(sessionId)) {
    sessions.set(sessionId, {
      history: []
    });
  }
  return sessions.get(sessionId);
}

export function createSession() {
  return crypto.randomUUID();
}

export function addToHistory(session, entry) {
  session.history.push(entry);

  // limit memory size
  if (session.history.length > 10) {
    session.history.shift();
  }
}