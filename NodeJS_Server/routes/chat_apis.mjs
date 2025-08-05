import express from 'express';
import CHAT_APIS from '../controllers/chat_controller.mjs';

import multer from 'multer';
import { fileURLToPath } from 'url';

// Get current file directory for ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configure multer storage
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    // Set destination to ../tempData/ relative to current file
    const tempFolderPath = path.resolve(__dirname, '../tempData');
    
    // Ensure the tempData folder exists
    if (!fs.existsSync(tempFolderPath)) {
      fs.mkdirSync(tempFolderPath, { recursive: true });
    }
    
    cb(null, tempFolderPath);
  },
  filename: (req, file, cb) => {
    // Keep original filename with timestamp to avoid conflicts
    const timestamp = Date.now();
    const sanitizedFilename = `${timestamp}_${file.originalname}`;
    cb(null, sanitizedFilename);
  }
});

// File filter to accept multiple document types
const fileFilter = (req, file, cb) => {
  // Define allowed file types
  const allowedMimeTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain'
  ];
  
  if (allowedMimeTypes.includes(file.mimetype)) {
    cb(null, true);
  } else {
    cb(new Error(`File type ${file.mimetype} is not supported`), false);
  }
};

// Create multer instance
const upload = multer({
  storage: storage,
  fileFilter: fileFilter,
  limits: {
    fileSize: 50 * 1024 * 1024, // 50MB limit per file
    files: 10 // Maximum 10 files per request
  }
});

// Export the multer middleware for use in routes
export const uploadMiddleware = upload.array('documents', 10);


const router = express.Router();

// Get all chats with basic information
router.get('/chats', CHAT_APIS.getAllChats);

// Get all chats for a specific user
router.get('/chats/user/:userId', CHAT_APIS.getUserChats);

// Get specific chat data by chatId with complete information
router.get('/chats/:chatId', CHAT_APIS.getChatById);

// Create a new chat for a user
router.post('/chats', CHAT_APIS.createNewChat);

// Append a new prompt to chat history
router.post('/chats/:chatId/prompt', CHAT_APIS.appendPromptToChat);

// Update the response in the last history item of a chat
router.put('/chats/:chatId/response', CHAT_APIS.appendResponseToChat);

// Get the latest history item from a chat
router.get('/chats/:chatId/latest', CHAT_APIS.getLatestHistoryItem);

// Delete a chat by chatId
router.delete('/chats/:chatId', CHAT_APIS.deleteChatById);

// Update the title of a chat by chatId
router.put('/chats/:chatId/title', CHAT_APIS.updateChatTitle);

// Upload a document to a specific chat
router.post('/chats/:chatId/documents', uploadMiddleware, CHAT_APIS.uploadDocuments);

export default router;
