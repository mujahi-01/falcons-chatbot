import { FALCON_SCHEMA } from "./schema.js";

export function validateFalconOutput(obj) {
  if (typeof obj !== "object" || obj === null) {
    return "Output is not an object";
  }

  for (const field of FALCON_SCHEMA.required) {
    if (!(field in obj)) {
      return `Missing required field: ${field}`;
    }
  }

  if (!FALCON_SCHEMA.properties.language.enum.includes(obj.language)) {
    return `Invalid language: ${obj.language}`;
  }

  if (typeof obj.filename !== "string" || !obj.filename.includes(".")) {
    return "Invalid filename";
  }

  if (typeof obj.code !== "string" || obj.code.trim() === "") {
    return "Code is empty";
  }

  if (typeof obj.explanation !== "string") {
    return "Explanation is invalid";
  }

  return null; // VALID
}