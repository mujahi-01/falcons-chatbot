import fs from "fs";
import os from "os";
import path from "path";
import { exec } from "child_process";
import { RUNTIMES } from "./runtime.js";

const TIMEOUT_MS = 10_000;

// very basic safety net (we harden later)
const FORBIDDEN_PATTERNS = [
  "rm -rf /",
  "shutdown",
  "reboot",
  ":(){:|:&};:"
];

export function executeArtifact(artifact) {
  const { language, filename, code, run } = artifact;

  if (!run) {
    return { skipped: true };
  }

  for (const bad of FORBIDDEN_PATTERNS) {
    if (code.includes(bad)) {
      throw new Error("Forbidden command detected");
    }
  }

  const runtime = RUNTIMES[language];
  if (!runtime) {
    throw new Error(`Unsupported language: ${language}`);
  }

  // temp isolated directory
  const workdir = fs.mkdtempSync(
    path.join(os.tmpdir(), "falcon-")
  );

  const filePath = path.join(workdir, filename);
  fs.writeFileSync(filePath, code, { mode: 0o755 });

  return new Promise((resolve, reject) => {
    exec(
      runtime.command(filePath),
      { timeout: TIMEOUT_MS, cwd: workdir },
      (error, stdout, stderr) => {
        if (error) {
          return reject({
            error: error.message,
            stderr
          });
        }

        resolve({
          stdout,
          stderr
        });
      }
    );
  });
}