import mongoose from 'mongoose';
import dotenv from 'dotenv';

dotenv.config();

/* Reading the DB Config Info from the Process Environment */
const config = {
  user: encodeURIComponent(process.env.DB_USERNAME),
  password: encodeURIComponent(process.env.DB_PASSWORD),
  clusterName: process.env.DB_CLUSTER_NAME.toLowerCase(),
  clusterId: process.env.DB_CLUSTER_ID,
  appName: process.env.DB_CLUSTER_NAME,
  dbName: process.env.DB_NAME, // Ensure this is set in your .env file
};

const url = `mongodb+srv://${config.user}:${config.password}@${config.clusterName}.${config.clusterId}.mongodb.net/${config.dbName}?retryWrites=true&w=majority&appName=${config.appName}`;
const clientOptions = {
  serverApi: {
    version: '1',
    strict: true,
    deprecationErrors: true
  },
  useNewUrlParser: true,
  useUnifiedTopology: true
};

async function connectToMongoDB() {
  try {
    await mongoose.connect(url, clientOptions);
    await mongoose.connection.db.admin().command({ ping: 1 });

    console.log('Connected successfully to MongoDB server');
  } catch (err) {
    await mongoose.disconnect();
    console.error('Failed to connect to MongoDB', err);
    return null;
  }
}

async function closeMongoDB() {
  await mongoose.disconnect();
  console.log('Closed MongoDB connection');
}

connectToMongoDB();

export {
  closeMongoDB,
};