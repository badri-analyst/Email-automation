export function errorHandler(error, _request, response, _next) {
  if (process.env.NODE_ENV !== 'production') {
    console.error(error);
  } else {
    console.error(`[${new Date().toISOString()}] ${error.status || 500} — ${error.message}`);
  }
  response.status(error.status || 500).json({ error: error.message || 'Unexpected server error' });
}
