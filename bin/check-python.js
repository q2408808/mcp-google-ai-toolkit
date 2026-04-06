#!/usr/bin/env node
/**
 * Post-install check: verify Python 3 and fastmcp are available.
 */
"use strict";

const { execSync } = require("child_process");

function check(cmd, label) {
  try {
    execSync(cmd, { encoding: "utf8", stdio: "pipe" });
    return true;
  } catch (_) {
    return false;
  }
}

const hasPython = check("python3 --version") || check("python --version");
if (!hasPython) {
  console.warn(
    "\n⚠️  [SocketsIO Google AI Toolkit] Python 3 not found.\n" +
    "   Install Python 3.9+ from https://python.org\n"
  );
  process.exit(0);
}

const python = check("python3 --version") ? "python3" : "python";
const hasFastmcp = check(`${python} -c "import fastmcp"`);
if (!hasFastmcp) {
  console.log(
    "\n📦 [SocketsIO Google AI Toolkit] Installing Python dependencies...\n"
  );
  try {
    const path = require("path");
    const req = path.join(__dirname, "..", "requirements.txt");
    execSync(`${python} -m pip install -r ${req}`, { stdio: "inherit" });
    console.log("✅ Dependencies installed.\n");
  } catch (err) {
    console.warn(
      "\n⚠️  Could not auto-install dependencies.\n" +
      `   Run manually: ${python} -m pip install fastmcp httpx\n`
    );
  }
} else {
  console.log("✅ [SocketsIO Google AI Toolkit] Python dependencies OK.\n");
}
