import express from 'express';
import { closeMongoDB } from './config/mongoDB.mjs';
import cors from 'cors';
import mainRouter from './routes/main_router.mjs';


const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.use('/api', mainRouter);

app.get('/', (req, res) => {
  res.send('Server is Up and Running! GG! Heelo World!');
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});

// Handle server close
process.on('SIGINT', async () => {
  console.log('Shutting down server...');
  await closeMongoDB();
  console.log('MongoDB connection closed.');
  process.exit(0);
});