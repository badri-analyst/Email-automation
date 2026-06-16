import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(__dirname, '..', '..');

const PYTHON_TIMEOUT_MS = 120_000;

export function runPython(moduleName, payload) {
  return new Promise((resolve, reject) => {
    const python = process.env.PYTHON_BIN || 'python';
    const runner = path.join(projectRoot, 'backend', 'services', 'python_runner.py');
    const child = spawn(python, [runner, moduleName], { cwd: projectRoot });
    let stdout = '';
    let stderr = '';

    // Kill the subprocess if it hangs longer than PYTHON_TIMEOUT_MS.
    const killTimer = setTimeout(() => {
      child.kill('SIGTERM');
      reject(new Error(`Python module ${moduleName} timed out after ${PYTHON_TIMEOUT_MS / 1000}s`));
    }, PYTHON_TIMEOUT_MS);

    child.stdout.on('data', (chunk) => { stdout += chunk.toString(); });
    child.stderr.on('data', (chunk) => {
      const text = chunk.toString();
      stderr += text;
      process.stderr.write(`[python:${moduleName}] ${text}`);
    });
    child.on('error', (err) => { clearTimeout(killTimer); reject(err); });
    child.on('close', (code) => {
      clearTimeout(killTimer);
      if (code !== 0) {
        reject(new Error(stderr || `Python module ${moduleName} failed`));
        return;
      }
      try {
        resolve(JSON.parse(stdout || '{}'));
      } catch (error) {
        reject(new Error(`Invalid Python JSON response: ${error.message}`));
      }
    });

    child.stdin.write(JSON.stringify(payload || {}));
    child.stdin.end();
  });
}
