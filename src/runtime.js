export const RUNTIMES = {
  bash: {
    ext: ".sh",
    command: (file) => `bash ${file}`
  },
  python: {
    ext: ".py",
    command: (file) => `python3 ${file}`
  },
  node: {
    ext: ".js",
    command: (file) => `node ${file}`
  },
  go: {
    ext: ".go",
    command: (file) => `go run ${file}`
  }
};