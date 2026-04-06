#!/usr/bin/env node
/**
 * SocketsIO Google AI Toolkit MCP Server — Node.js wrapper
 * Launches the Python FastMCP server.
 */
"use strict";

const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");

const SERVER_PY = path.join(__dirname, "..", "server.py");
const REQUIREMENTS = path.join(__dirname, "..", "requirements.txt");

// ─── Check API key ───
if (!process.env.SOCKETSIO_API_KEY) {
  console.error(
    "[SocketsIO Google AI Toolkit] ERROR: SOCKETSIO_API_KEY is not set.\n" +
    "Get your free API key at https://socketsio.com/signup\n" +
    "Then set it: export SOCKETSIO_API_KEY=your-key-here"
  );
  process.exit(1);
}

// ─── Find Python ───
function findPython() {
  const candidates = ["python3", "python"];
  for (const cmd of candidates) {
    try {
      const result = require("child_process").execSync(`${cmd} --version 2>&1`, { encoding: "utf8" });
      if (result.includes("Python 3")) return cmd;
    } catch (_) {}
  }
  return null;
}

const python = findPython();
if (!python) {
  console.error(
    "[SocketsIO Google AI Toolkit] ERROR: Python 3 not found.\n" +
    "Install Python 3.9+ from https://python.org"
  );
  process.exit(1);
}

// ─── Check fastmcp ───
try {
  require("child_process").execSync(`${python} -c "import fastmcp"`, { encoding: "utf8" });
} catch (_) {
  console.error(
    "[SocketsIO Google AI Toolkit] ERROR: fastmcp not installed.\n" +
    `Run: ${python} -m pip install -r ${REQUIREMENTS}`
  );
  process.exit(1);
}

// ─── Launch server ───
const proc = spawn(python, [SERVER_PY], {
  stdio: "inherit",
  env: process.env,
});

proc.on("error", (err) => {
  console.error("[SocketsIO Google AI Toolkit] Failed to start server:", err.message);
  process.exit(1);
});

proc.on("exit", (code) => {
  process.exit(code || 0);
});

// Forward signals
["SIGINT", "SIGTERM"].forEach((sig) => {
  process.on(sig, () => {
    proc.kill(sig);
  });
});
