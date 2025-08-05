import Chat from '../models/chat.mjs';

/**
 * Get all chats with basic information only
 * Returns: Array of {chatId, userId, title, updatedAt}
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
export const getAllChats = async (req, res) => {
  try {
    // Fetch all chats but only select specific fields
    // Exclude the history field to avoid returning internal data
    const chats = await Chat.find({})
      .select('_id userId title updatedAt')
      .sort({ updatedAt: -1 }) // Sort by most recently updated first
      .lean(); // Use lean() for better performance since we don't need full mongoose documents

    // Transform the data to match the required format
    const transformedChats = chats.map(chat => ({
      chatId: chat._id,
      userId: chat.userId,
      title: chat.title,
      updatedAt: chat.updatedAt
    }));

    // Return success response with the chat data
    res.status(200).json({
      success: true,
      message: 'Chats fetched successfully',
      data: transformedChats,
      count: transformedChats.length
    });

  } catch (error) {
    console.error('Error fetching chats:', error);
    
    // Return error response
    res.status(500).json({
      success: false,
      message: 'Failed to fetch chats',
      error: error.message
    });
  }
};

/**
 * Get all chats for a specific user with basic information only
 * Returns: Array of {chatId, userId, title, updatedAt}
 * @param {Object} req - Express request object (expects userId in params)
 * @param {Object} res - Express response object
 */
export const getUserChats = async (req, res) => {
  try {
    const { userId } = req.params;

    if (!userId) {
      return res.status(400).json({
        success: false,
        message: 'User ID is required'
      });
    }

    // Fetch chats for specific user, excluding history
    const chats = await Chat.find({ userId })
      .select('_id userId title updatedAt')
      .sort({ updatedAt: -1 })
      .lean();

    // Transform the data to match the required format
    const transformedChats = chats.map(chat => ({
      chatId: chat._id,
      userId: chat.userId,
      title: chat.title,
      updatedAt: chat.updatedAt
    }));

    res.status(200).json({
      success: true,
      message: 'User chats fetched successfully',
      data: transformedChats,
      count: transformedChats.length
    });

  } catch (error) {
    console.error('Error fetching user chats:', error);
    
    res.status(500).json({
      success: false,
      message: 'Failed to fetch user chats',
      error: error.message
    });
  }
};

/**
 * Get specific chat data by chatId with complete information including history
 * Returns: Complete chat object with all data
 * @param {Object} req - Express request object (expects chatId in params)
 * @param {Object} res - Express response object
 */
export const getChatById = async (req, res) => {
  try {
    const { chatId } = req.params;

    if (!chatId) {
      return res.status(400).json({
        success: false,
        message: 'Chat ID is required'
      });
    }

    // Fetch complete chat data including history
    const chat = await Chat.findById(chatId).lean();

    if (!chat) {
      return res.status(404).json({
        success: false,
        message: 'Chat not found'
      });
    }

    // Transform the response to include chatId instead of _id
    const transformedChat = {
      chatId: chat._id,
      userId: chat.userId,
      title: chat.title,
      history: chat.history,
      docChunkIds: chat.docChunkIds,
      createdAt: chat.createdAt,
      updatedAt: chat.updatedAt
    };

    res.status(200).json({
      success: true,
      message: 'Chat fetched successfully',
      data: transformedChat
    });

  } catch (error) {
    console.error('Error fetching chat by ID:', error);
    
    res.status(500).json({
      success: false,
      message: 'Failed to fetch chat',
      error: error.message
    });
  }
};

/**
 * Create a new chat for a user
 * Takes userId from request body and creates a new chat
 * @param {Object} req - Express request object (expects userId and title in body)
 * @param {Object} res - Express response object
 */
export const createNewChat = async (req, res) => {
  try {
    const { userId, title } = req.body;

    // Validate required fields
    if (!userId) {
      return res.status(400).json({
        success: false,
        message: 'User ID is required'
      });
    }

    if (!title || title.trim() === '') {
      return res.status(400).json({
        success: false,
        message: 'Chat title is required'
      });
    }

    // Create new chat
    const newChat = new Chat({
      userId,
      title: title.trim(),
      history: [], // Start with empty history
      docChunkIds: docChunkIds || [] // Include docChunkIds if provided, otherwise empty array
    });

    // Save to database
    const savedChat = await newChat.save();

    // Transform response to match expected format
    const transformedChat = {
      chatId: savedChat._id,
      userId: savedChat.userId,
      title: savedChat.title,
      history: savedChat.history,
      docChunkIds: savedChat.docChunkIds,
      createdAt: savedChat.createdAt,
      updatedAt: savedChat.updatedAt
    };

    res.status(201).json({
      success: true,
      message: 'Chat created successfully',
      data: transformedChat
    });

  } catch (error) {
    console.error('Error creating new chat:', error);
    
    res.status(500).json({
      success: false,
      message: 'Failed to create chat',
      error: error.message
    });
  }
};

// ...existing code...

/**
 * Append a new prompt to chat history
 * Creates a new history item with prompt data and empty response
 * @param {Object} req - Express request object (expects chatId in params, prompt data in body)
 * @param {Object} res - Express response object
 */
export const appendPromptToChat = async (req, res) => {
  try {
    const { chatId } = req.params;
    const { text, docs } = req.body;

    // Validate required fields
    if (!chatId) {
      return res.status(400).json({
        success: false,
        message: 'Chat ID is required'
      });
    }

    if (!text || text.trim() === '') {
      return res.status(400).json({
        success: false,
        message: 'Prompt text is required'
      });
    }

    // Validate docs array if provided
    let processedDoc = null;
    if (docs && docs.length > 0) {
      // Take the first document from the array
      const doc = docs[0];
      
      // Validate document structure
      if (!doc.filename || !doc.size || !doc.fileType) {
        return res.status(400).json({
          success: false,
          message: 'Document must contain filename, size, and fileType'
        });
      }

      processedDoc = {
        filename: doc.filename,
        size: doc.size,
        fileType: doc.fileType
      };
    }

    // Create new history item with prompt and empty response
    const newHistoryItem = {
      prompt: {
        text: text.trim(),
        doc: processedDoc
      },
      response: {
        text: '', // Empty response initially
        citations: []
      }
    };

    // Find and update the chat by pushing new history item
    const updatedChat = await Chat.findByIdAndUpdate(
      chatId,
      { 
        $push: { history: newHistoryItem },
        $set: { updatedAt: new Date() }
      },
      { new: true, runValidators: true }
    ).lean();

    if (!updatedChat) {
      return res.status(404).json({
        success: false,
        message: 'Chat not found'
      });
    }

    // Get the newly added history item (last item in array)
    const addedHistoryItem = updatedChat.history[updatedChat.history.length - 1];

    res.status(200).json({
      success: true,
      message: 'Prompt added to chat history successfully',
      data: {
        chatId: updatedChat._id,
        historyIndex: updatedChat.history.length - 1,
        addedItem: addedHistoryItem
      }
    });

  } catch (error) {
    console.error('Error appending prompt to chat:', error);
    
    res.status(500).json({
      success: false,
      message: 'Failed to append prompt to chat',
      error: error.message
    });
  }
};

/**
 * Update the response in the last history item of a chat
 * Updates the response field of the most recent history item
 * @param {Object} req - Express request object (expects chatId in params, response data in body)
 * @param {Object} res - Express response object
 */
export const appendResponseToChat = async (req, res) => {
  try {
    const { chatId } = req.params;
    const { text, citations } = req.body;

    // Validate required fields
    if (!chatId) {
      return res.status(400).json({
        success: false,
        message: 'Chat ID is required'
      });
    }

    if (!text || text.trim() === '') {
      return res.status(400).json({
        success: false,
        message: 'Response text is required'
      });
    }

    // Validate citations array if provided
    let processedCitations = [];
    if (citations && Array.isArray(citations)) {
      processedCitations = citations.map(citation => {
        if (!citation.filename || citation.pageNo === undefined) {
          throw new Error('Each citation must contain filename and pageNo');
        }
        return {
          filename: citation.filename,
          pageNo: citation.pageNo
        };
      });
    }

    // First, check if chat exists and has history items
    const existingChat = await Chat.findById(chatId).lean();
    
    if (!existingChat) {
      return res.status(404).json({
        success: false,
        message: 'Chat not found'
      });
    }

    if (!existingChat.history || existingChat.history.length === 0) {
      return res.status(400).json({
        success: false,
        message: 'No history items found in chat. Add a prompt first.'
      });
    }

    // Update the response in the last history item
    const lastHistoryIndex = existingChat.history.length - 1;
    
    const updatedChat = await Chat.findByIdAndUpdate(
      chatId,
      { 
        $set: { 
          [`history.${lastHistoryIndex}.response.text`]: text.trim(),
          [`history.${lastHistoryIndex}.response.citations`]: processedCitations,
          updatedAt: new Date()
        }
      },
      { new: true, runValidators: true }
    ).lean();

    // Get the updated history item
    const updatedHistoryItem = updatedChat.history[lastHistoryIndex];

    res.status(200).json({
      success: true,
      message: 'Response updated in chat history successfully',
      data: {
        chatId: updatedChat._id,
        historyIndex: lastHistoryIndex,
        updatedItem: updatedHistoryItem
      }
    });

  } catch (error) {
    console.error('Error appending response to chat:', error);
    
    res.status(500).json({
      success: false,
      message: 'Failed to append response to chat',
      error: error.message
    });
  }
};

/**
 * Get the latest history item from a chat (for checking current state)
 * @param {Object} req - Express request object (expects chatId in params)
 * @param {Object} res - Express response object
 */
export const getLatestHistoryItem = async (req, res) => {
  try {
    const { chatId } = req.params;

    if (!chatId) {
      return res.status(400).json({
        success: false,
        message: 'Chat ID is required'
      });
    }

    const chat = await Chat.findById(chatId)
      .select('_id history')
      .lean();

    if (!chat) {
      return res.status(404).json({
        success: false,
        message: 'Chat not found'
      });
    }

    if (!chat.history || chat.history.length === 0) {
      return res.status(200).json({
        success: true,
        message: 'No history items found',
        data: null
      });
    }

    const latestItem = chat.history[chat.history.length - 1];

    res.status(200).json({
      success: true,
      message: 'Latest history item fetched successfully',
      data: {
        chatId: chat._id,
        historyIndex: chat.history.length - 1,
        historyItem: latestItem
      }
    });

  } catch (error) {
    console.error('Error fetching latest history item:', error);
    
    res.status(500).json({
      success: false,
      message: 'Failed to fetch latest history item',
      error: error.message
    });
  }
};