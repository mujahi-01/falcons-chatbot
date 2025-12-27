export const FALCON_SCHEMA = {
  type: "object",
  required: ["language", "filename", "run", "code", "explanation"],
  properties: {
    language: {
      type: "string",
      enum: ["bash", "python", "node", "go"]
    },
    filename: {
      type: "string",
      minLength: 1
    },
    run: {
      type: "boolean"
    },
    code: {
      type: "string",
      minLength: 1
    },
    explanation: {
      type: "string",
      minLength: 1
    }
  },
  additionalProperties: false
};