import mongoose from 'mongoose';

// Define the document schema for file attachments
const documentSchema = new mongoose.Schema({
  filename: {
    type: String,
    required: true
  },
  size: {
    type: Number,
    required: true
  },
  fileType: {
    type: String,
    required: true
  }
}, { _id: false });

// Define the citation schema
const citationSchema = new mongoose.Schema({
  filename: {
    type: String,
    required: true
  },
  pageNo: {
    type: Number,
    required: true
  }
}, { _id: false });

// Define the prompt schema
const promptSchema = new mongoose.Schema({
  text: {
    type: String,
    required: true
  },
  doc: {
    type: documentSchema,
    required: false
  }
}, { _id: false });

// Define the response schema
const responseSchema = new mongoose.Schema({
  text: {
    type: String,
    required: true
  },
  citations: {
    type: [citationSchema],
    default: []
  }
}, { _id: false });

// Define the history item schema
const historyItemSchema = new mongoose.Schema({
  prompt: {
    type: promptSchema,
    required: true
  },
  response: {
    type: responseSchema,
    required: true
  }
}, { _id: false });

// Define the main Chat schema
const chatSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  title: {
    type: String,
    required: true,
    default: 'New Chat',
    trim: true
  },
  history: {
    type: [historyItemSchema],
    default: []
  },
  docChunkIds: {
    type: [String],
    default: [],
    index: true // Add index for efficient querying by document chunks
  }
}, {
  timestamps: true // This automatically adds createdAt and updatedAt fields
});

// Create indexes for better query performance
chatSchema.index({ userId: 1 });
chatSchema.index({ userId: 1, updatedAt: -1 });

// Export the Chat model
const Chat = mongoose.model('Chat', chatSchema);

export default Chat;