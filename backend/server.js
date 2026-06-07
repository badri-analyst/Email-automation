import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import apiRoutes from './routes/index.js';
import { errorHandler } from './middleware/errorHandler.js';

const app = express();
const port = process.env.PORT || 8080;

app.use(helmet());
const allowedOrigin = process.env.FRONTEND_ORIGIN;
if (!allowedOrigin && process.env.NODE_ENV === 'production') {
  throw new Error('FRONTEND_ORIGIN must be set in production. Add it to your Render environment variables.');
}
app.use(cors({ origin: allowedOrigin || 'http://localhost:5173', credentials: true }));
app.use(express.json({ limit: '2mb' }));
app.use(morgan(process.env.NODE_ENV === 'production' ? 'combined' : 'dev'));
app.use('/api', apiRoutes);
app.use(errorHandler);

app.listen(port, () => {
  console.log(`AI outreach backend listening on ${port}`);
});
