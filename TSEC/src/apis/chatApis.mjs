import axios from 'axios';
import FormData from 'form-data';
import fs from 'fs';
import { BASE_URL } from './config.mjs';

// Get all chats with basic information
export const getAllChats = async () => {
  axios.get(`${BASE_URL}/api/chats`)
  .then((response) => {
    console.log(JSON.stringify(response.data));
  })
  .catch((error) => {
    console.log(error);
  })
};

// Get all chats for a specific user
export const getUserChats = async (userId) => {
  axios.get(`${BASE_URL}/api/chats/user/${userId}`)
  .then((response) => {
    console.log(JSON.stringify(response.data));
  })
  .catch((error) => {
    console.log(error);
  })
};

// Get specific chat data by chatId with complete information
export const getChatById = async (chatId) => {
  axios.get(`${BASE_URL}/api/chats/${chatId}`)
  .then((response) => {
    console.log(JSON.stringify(response.data));
  })
  .catch((error) => {
    console.log(error);
  })
};

// Create a new chat for a user
export const createNewChat = async (userId) => {
  let data = {
    userId: userId,
  };

  axios.post(`${BASE_URL}/api/chats`, data, {
    headers: { 
      'Content-Type': 'application/json'
    }
  })
  .then((response) => {
    console.log(JSON.stringify(response.data));
  })
  .catch((error) => {
    console.log(error);
  })
};

// Add a prompt to a chat, including a document upload
export const addPromptToChat = async (chatId, text, doc) => {
  let data = new FormData();
  data.append('text', text);
  data.append('doc', fs.createReadStream(doc));

  let config = {
    method: 'post',
    maxBodyLength: Infinity,
    url: `${BASE_URL}/api/chats/${chatId}/prompt`,
    headers: { 
      ...data.getHeaders()
    },
    data : data
  };

  axios.request(config)
  .then((response) => {
    console.log(JSON.stringify(response.data));
  })
  .catch((error) => {
    console.log(error);
  })
};

// Update the response in the last history item of a chat
export const appendResponseToChat = async (chatId, response) => {
  let data = {
    response: response
  };

  axios.put(`${BASE_URL}/api/chats/${chatId}/response`, data, {
    headers: { 
      'Content-Type': 'application/json'
    }
  })
  .then((response) => {
    console.log(JSON.stringify(response.data));
  })
  .catch((error) => {
    console.log(error);
  })
};

// Get the latest history item from a chat
export const getLatestHistoryItem = async (chatId) => {
  axios.get(`${BASE_URL}/api/chats/${chatId}/latest`)
  .then((response) => {
    console.log(JSON.stringify(response.data));
  })
  .catch((error) => {
    console.log(error);
  })
};

// Delete a specific chat by chatId
export const deleteChatById = async (chatId) => {
  axios.delete(`${BASE_URL}/api/chats/${chatId}`)
  .then((response) => {
    console.log(JSON.stringify(response.data));
  })
  .catch((error) => {
    console.log(error);
  })
};

// Update the title of a specific chat by chatId
export const updateChatTitle = async (chatId, newTitle) => {
  let data = {
    title: newTitle
  };

  axios.put(`${BASE_URL}/api/chats/${chatId}/title`, data, {
    headers: { 
      'Content-Type': 'application/json'
    }
  })
  .then((response) => {
    console.log(JSON.stringify(response.data));
  })
  .catch((error) => {
    console.log(error);
  })
};

const CHAT_APIS = {
  addPromptToChat,
  getAllChats,
  getUserChats,
  getChatById,
  createNewChat,
  appendResponseToChat,
  getLatestHistoryItem,
  deleteChatById
};

export default CHAT_APIS;

