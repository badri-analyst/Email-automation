import { createReadStream, existsSync, statSync } from 'fs';
import { createServer } from 'http';
import { extname, join, resolve } from 'path';

const port = process.env.FRONTEND_PORT || 5173;
const root = resolve('dist');
const mime = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.json': 'application/json',
};

createServer((request, response) => {
  const urlPath = decodeURIComponent((request.url || '/').split('?')[0]);
  const requested = resolve(join(root, urlPath));
  let filePath = requested.startsWith(root) && existsSync(requested) ? requested : join(root, 'index.html');
  if (existsSync(filePath) && statSync(filePath).isDirectory()) {
    filePath = join(filePath, 'index.html');
  }
  response.setHeader('Content-Type', mime[extname(filePath)] || 'application/octet-stream');
  createReadStream(filePath).pipe(response);
}).listen(port, () => {
  console.log(`Frontend available at http://localhost:${port}`);
});
