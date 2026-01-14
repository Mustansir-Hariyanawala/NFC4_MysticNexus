import { useState, useRef, useEffect } from 'react';
import { Send, Upload, ChevronLeft, ChevronRight, FileText, Image, Video, File, X, Mic, MicOff, Loader2, Trash2 } from 'lucide-react';
import axios from 'axios';
import CHAT_APIS from '../apis/chatApis.mjs';
// import { Link } from 'react-router-dom'; // Remove this import for now

const ChatComponent = () => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [currentChatTitle, setCurrentChatTitle] = useState('New Chat');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isListening, setIsListening] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  const [interimTranscript, setInterimTranscript] = useState('');
  const recognitionRef = useRef(null);
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  // Load chat history on component mount
  useEffect(() => {
    loadChatHistory();
  }, []);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const loadChatHistory = async () => {
    try {
      const response = await CHAT_APIS.getUserChats(sessionStorage.getItem('user_id') );
      history = response.data || [];

      setChatHistory(history.map(chat => ({
        id: chat._id,
        title: chat.title,
        timestamp: new Date(chat.updated_at).toLocaleDateString(),
        updated_at: chat.updated_at
      })));
      
    } catch (error) {
      console.error('Failed to load chat history:', error.response?.data || error.message);
      // Fallback to demo data
      setChatHistory([
        { id: 1, title: 'RAG Chat about Machine Learning', description: 'Discussion about ML concepts', timestamp: '2024-03-15' },
        { id: 2, title: 'Document Analysis', description: 'PDF analysis session', timestamp: '2024-01-14' },
        { id: 3, title: 'Image Processing', description: 'Image analysis chat', timestamp: '2024-01-13' }
      ]);
    }
  };

  const loadChat = async (chatId) => {
    try {
      setIsLoading(true);
      const response = await CHAT_APIS.getChatById(chatId);
      
      if (!response.data) {
        console.error('Chat not found or empty');
        return;
      }
      
      const chatData = response.data;
      setCurrentChatId(chatId);
      setCurrentChatTitle(chatData.title);
      
      // Convert MongoDB format to component format
      const convertedMessages = [];
      chatData.history.forEach((exchange, index) => {
        // Add user message
        convertedMessages.push({
          id: `${chatId}_prompt_${index}`,
          type: 'user',
          text: exchange.prompt.text,
          files: exchange.prompt.doc ? [{
            id: `doc_${index}`,
            name: exchange.prompt.doc.filename,
            type: exchange.prompt.doc.file_type,
            size: exchange.prompt.doc.file_size,
            upload_timestamp: exchange.prompt.doc.upload_timestamp
          }] : [],
          timestamp: new Date(exchange.prompt.timestamp).toLocaleTimeString(),
          status: exchange.status
        });

        // Add AI response if it exists
        if (exchange.response) {
          convertedMessages.push({
            id: `${chatId}_response_${index}`,
            type: 'ai',
            text: exchange.response.text,
            citations: exchange.response.citations || [],
            doc_chunk_ids: exchange.response.doc_chunk_ids || [],
            processing_time: exchange.response.processing_time,
            timestamp: new Date(exchange.response.timestamp).toLocaleTimeString(),
            status: exchange.status
          });
        } else if (exchange.status === 'pending') {
          // Show loading state for pending responses
          convertedMessages.push({
            id: `${chatId}_response_${index}`,
            type: 'ai',
            text: '',
            timestamp: '',
            status: 'pending',
            isLoading: true
          });
        }
      });
      
      setMessages(convertedMessages);
      
    } catch (error) {
      console.error('Failed to load chat:', error.response?.data || error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const deleteChat = async (chatId) => {
    try {
      await CHAT_APIS.deleteChatById(chatId);

      // Remove chat from history
      setChatHistory(prev => prev.filter(chat => chat.id !== chatId));
      
      // If the deleted chat was the current one, clear the current chat
      if (currentChatId === chatId) {
        setCurrentChatId(null);
        setCurrentChatTitle('New Chat');
        setMessages([]);
        setUploadedFiles([]);
      }
      
    } catch (error) {
      console.error('Failed to delete chat:', error.response?.data || error.message);
      // You could add a toast notification here for user feedback
      alert('Failed to delete chat. Please try again.');
    }
  };

  const createNewChat = async () => {
    try {
      setIsLoading(true);
      
      // Make POST request to create new chat
      const userId = sessionStorage.getItem('user_id');
      const response = await CHAT_APIS.createNewChat(userId);

      if (!response.data) {
        console.error('Failed to create new chat: No data returned');
        return;
      }

      const newChat = response.data;
      
      // Update local state with the new chat
      setCurrentChatId(newChat._id || newChat.id);
      setCurrentChatTitle(newChat.title || 'New Chat');
      setMessages([]);
      setUploadedFiles([]);
      
      // Add the new chat to chat history
      const newChatHistoryItem = {
        id: newChat._id || newChat.id,
        title: newChat.title || 'New Chat',
        description: newChat.description || 'New conversation started',
        timestamp: new Date(newChat.created_at || newChat.updated_at || Date.now()).toLocaleDateString(),
        updated_at: newChat.updated_at || new Date().toISOString()
      };
      
      setChatHistory(prev => [newChatHistoryItem, ...prev]);
      
    } catch (error) {
      console.error('Failed to create new chat:', error.response?.data || error.message);
      
      // Fallback to local-only new chat if API fails
      setCurrentChatId(null);
      setCurrentChatTitle('New Chat');
      setMessages([]);
      setUploadedFiles([]);
      
      // You could add a toast notification here for user feedback
      alert('Failed to create new chat on server. Working in local mode.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteChat = (e, chatId) => {
    e.stopPropagation(); // Prevent chat selection when clicking delete
    if (window.confirm('Are you sure you want to delete this chat? This action cannot be undone.')) {
      deleteChat(chatId);
    }
  };

  // Speech recognition setup
  useEffect(() => {
    if (!SpeechRecognition) return;

    if (!recognitionRef.current) {
      recognitionRef.current = new SpeechRecognition();
    }

    const recognition = recognitionRef.current;

    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onresult = (event) => {
      let interim = '';
      let final = '';
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          final += event.results[i][0].transcript;
        } else {
          interim += event.results[i][0].transcript;
        }
      }

      if (final) {
        setInputText(prev => (prev + ' ' + final).trim());
        setInterimTranscript('');
      } else {
        setInterimTranscript(interim);
      }
    };

    recognition.onerror = (event) => {
      console.error("Speech recognition error", event.error);
      setIsListening(false);
      recognition.stop();
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    return () => {
      recognition.onresult = null;
      recognition.onerror = null;
      recognition.onend = null;
    };
  }, []);

  const toggleListening = () => {
    const recognition = recognitionRef.current;
    if (!recognition) return;

    if (isListening) {
      recognition.stop();
      setIsListening(false);
    } else {
      recognition.start();
      setIsListening(true);
      setInterimTranscript('');
    }
  };

  const getFileIcon = (fileType) => {
    if (fileType.startsWith('image/')) return <Image className="w-4 h-4" />;
    if (fileType.startsWith('video/')) return <Video className="w-4 h-4" />;
    if (fileType === 'application/pdf') return <FileText className="w-4 h-4" />;
    return <File className="w-4 h-4" />;
  };

  const handleFileUpload = (files) => {
    const newFiles = Array.from(files).map(file => ({
      id: Date.now() + Math.random(),
      name: file.name,
      type: file.type,
      size: file.size,
      file: file
    }));
    setUploadedFiles(prev => [...prev, ...newFiles]);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer?.files?.length) {
      handleFileUpload(e.dataTransfer.files);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const removeFile = (fileId) => {
    setUploadedFiles(prev => prev.filter(file => file.id !== fileId));
  };

  const sendMessage = async () => {
    if (!inputText.trim() && uploadedFiles.length === 0) return;

    // Check if we have a current chat ID
    if (!currentChatId) {
      console.error('No chat ID available. Please select or create a chat first.');
      return;
    }

    setIsLoading(true);
    const messageId = Date.now();
    
    // Create user message
    const userMessage = {
      id: messageId,
      type: 'user',
      text: inputText,
      files: [...uploadedFiles],
      timestamp: new Date().toLocaleTimeString(),
      status: 'completed'
    };
    
    // Add user message to UI
    setMessages(prev => [...prev, userMessage]);
    
    // Add loading AI message
    const loadingMessage = {
      id: messageId + 1,
      type: 'ai',
      text: '',
      timestamp: '',
      status: 'pending',
      isLoading: true
    };
    setMessages(prev => [...prev, loadingMessage]);

    // Prepare request data
    const requestData = {
      prompt: {
        text: inputText,
        doc: uploadedFiles.length > 0 ? {
          filename: uploadedFiles[0].name,
          file_size: uploadedFiles[0].size,
          file_type: uploadedFiles[0].type,
          upload_timestamp: new Date().toISOString()
        } : null,
        timestamp: new Date().toISOString()
      }
    };

    // Clear input
    const currentInput = inputText;
    const currentFiles = [...uploadedFiles];
    setInputText('');
    setUploadedFiles([]);

    try {
      // Always use the specific chat endpoint
      const endpoint = `/api/chat/${currentChatId}/prompt`;
      
      const response = await CHAT_APIS.addPromptToChat(currentChatId, requestData.prompt.text, currentFiles[0]?.file);

      const result = response.data;
      
      // Replace loading message with actual response
      setMessages(prev => prev.map(msg => 
        msg.id === messageId + 1 ? {
          ...msg,
          text: result.response?.text || result.text || 'Response received',
          citations: result.response?.citations || result.citations || [],
          doc_chunk_ids: result.response?.doc_chunk_ids || result.doc_chunk_ids || [],
          processing_time: result.response?.processing_time || result.processing_time,
          timestamp: result.response?.timestamp 
            ? new Date(result.response.timestamp).toLocaleTimeString()
            : new Date().toLocaleTimeString(),
          status: 'completed',
          isLoading: false
        } : msg
      ));
      
    } catch (error) {
      console.error('Error sending message:', error.response?.data || error.message);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to send message';
      
      // Restore input and files on error
      setInputText(currentInput);
      setUploadedFiles(currentFiles);
      
      // Replace loading message with error
      setMessages(prev => prev.map(msg => 
        msg.id === messageId + 1 ? {
          ...msg,
          text: `Sorry, I encountered an error: ${errorMessage}. Please try again.`,
          timestamp: new Date().toLocaleTimeString(),
          status: 'error',
          isLoading: false
        } : msg
      ));
    } finally {
      setIsLoading(false);
    }
  };

  const summarizeFiles = async () => {
    if (uploadedFiles.length === 0) return;
    
    const summaryText = `Please summarize the uploaded file${uploadedFiles.length > 1 ? 's' : ''}: ${uploadedFiles.map(f => f.name).join(', ')}`;
    setInputText(summaryText);
    await sendMessage();
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="flex h-screen bg-gray-900 mt-28" 
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}>
      
      {/* Sidebar */}
      <div className={`bg-gray-800 shadow-2xl transition-all duration-300 ${sidebarCollapsed ? 'w-0' : 'w-80'} border-r border-green-500/20`}>
        <div className={`h-full ${sidebarCollapsed ? 'hidden' : 'block'}`}>
          <div className="p-4 bg-gradient-to-r from-green-400 to-green-600 text-black">
            <h2 className="text-lg font-bold">Chat History</h2>
            <button
              onClick={createNewChat}
              className="mt-2 px-3 py-1 bg-black/20 rounded text-sm hover:bg-black/30 transition-all"
            >
              + New Chat
            </button>
          </div>
          <div className="p-4 space-y-3 overflow-y-auto h-full">
            {chatHistory.map(chat => (
              <div 
                key={chat.id} 
                onClick={() => loadChat(chat.id)}
                className={`p-3 rounded-lg cursor-pointer transition-all border relative group ${
                  currentChatId === chat.id
                    ? 'bg-gradient-to-r from-green-500/30 to-green-400/30 border-green-400/50'
                    : 'bg-gray-700 hover:bg-gradient-to-r hover:from-green-500/20 hover:to-green-400/20 border-green-500/10 hover:border-green-400/30'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-green-400 truncate">{chat.title}</div>
                    {chat.description && (
                      <div className="text-xs text-gray-400 truncate mt-1">{chat.description}</div>
                    )}
                    <div className="text-sm text-gray-400">{chat.timestamp}</div>
                  </div>
                  
                  {/* Delete button - appears on hover */}
                  <button
                    onClick={(e) => handleDeleteChat(e, chat.id)}
                    className="opacity-0 group-hover:opacity-100 p-1 text-red-400 hover:text-red-300 hover:bg-red-400/10 rounded transition-all ml-2 flex-shrink-0"
                    title="Delete chat"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
            
            <br />
            <a 
              href="/profchat" 
              className="block p-3 rounded-lg bg-gray-700 hover:bg-gradient-to-r hover:from-green-500/20 hover:to-green-400/20 border border-green-500/10 hover:border-green-400/30 cursor-pointer transition-all"
            >
              <div className="font-medium text-green-400">Professional Chat</div>
              <div className="text-sm text-gray-400">Start a new professional conversation</div>
            </a>
          </div>
        </div>
      </div>

      {/* Sidebar Toggle Button */}
      <button
        onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
        className="absolute left-0 top-1/2 transform -translate-y-1/2 bg-gradient-to-r from-green-400 to-green-600 text-black p-2 rounded-r-lg shadow-lg hover:from-green-300 hover:to-green-500 transition-all z-10"
        style={{ left: sidebarCollapsed ? '0' : '320px' }}
      >
        {sidebarCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
      </button>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-gray-800 shadow-lg border-b border-green-500/20 p-4">
          <h1 className="text-xl font-bold text-green-400 flex items-center space-x-2">
            <span>{currentChatTitle}</span>
            {isLoading && <Loader2 className="w-5 h-5 animate-spin" />}
          </h1>
        </div>

        {/* Messages Area */}
        <div 
          className={`flex-1 overflow-y-auto p-4 space-y-4 bg-gray-900 ${isDragging ? 'bg-green-900/20 border-2 border-dashed border-green-400' : ''}`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
        >
          {isDragging && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-green-400">
                <Upload className="w-12 h-12 mx-auto mb-2 animate-bounce" />
                <p className="text-lg font-bold">&gt; DROP FILES TO UPLOAD</p>
                <p className="text-sm text-green-300">DRAG_AND_DROP.INITIATED</p>
              </div>
            </div>
          )}
          
          {messages.map(message => (
            <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg border ${
                message.type === 'user' 
                  ? 'bg-gradient-to-r from-green-600 to-green-500 text-black border-green-400 shadow-lg shadow-green-500/20' 
                  : 'bg-gray-800 text-green-300 border-green-500/30 shadow-lg'
              }`}>
                {message.isLoading ? (
                  <div className="flex items-center space-x-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span className="text-sm">Processing...</span>
                  </div>
                ) : (
                  <>
                    {message.text && <p className="text-sm">{message.text}</p>}
                    
                    {/* Citations */}
                    {message.citations && message.citations.length > 0 && (
                      <div className="mt-2 text-xs">
                        <div className="text-green-400 font-semibold">Sources:</div>
                        {message.citations.map((citation, idx) => (
                          <div key={idx} className="text-green-300/80">• {citation}</div>
                        ))}
                      </div>
                    )}
                    
                    {/* Processing time for AI responses */}
                    {message.processing_time && (
                      <div className="text-xs text-green-500/70 mt-1">
                        Processed in {message.processing_time}s
                      </div>
                    )}
                  </>
                )}
                
                {message.files && message.files.length > 0 && (
                  <div className="mt-2 space-y-1">
                    {message.files.map(file => (
                      <div key={file.id} className="flex items-center space-x-2 text-xs bg-black/30 rounded p-1 border border-green-500/20">
                        {getFileIcon(file.type)}
                        <span className="truncate text-green-300">{file.name}</span>
                        <span className="text-green-500 text-xs">{formatFileSize(file.size)}</span>
                      </div>
                    ))}
                  </div>
                )}
                
                {message.timestamp && (
                  <div className={`text-xs mt-1 ${message.type === 'user' ? 'text-black/70' : 'text-green-500'}`}>
                    {message.timestamp}
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* File Upload Preview */}
        {uploadedFiles.length > 0 && (
          <div className="bg-gray-800 border-t border-green-500/20 p-3">
            <div className="text-sm font-bold text-green-400 mb-2">Uploaded Files ({uploadedFiles.length})</div>
            <div className="space-y-2 max-h-32 overflow-y-auto">
              {uploadedFiles.map(file => (
                <div key={file.id} className="flex items-center justify-between bg-gray-700 p-2 rounded border border-green-500/20">
                  <div className="flex items-center space-x-2 flex-1 min-w-0">
                    <span className="text-green-400">{getFileIcon(file.type)}</span>
                    <div className="min-w-0 flex-1">
                      <div className="text-sm text-green-300 truncate">{file.name}</div>
                      <div className="text-xs text-green-500">{formatFileSize(file.size)}</div>
                    </div>
                  </div>
                  <button
                    onClick={() => removeFile(file.id)}
                    className="text-red-400 hover:text-red-300 ml-2 hover:bg-red-400/10 p-1 rounded transition-all"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="bg-gray-800 border-t border-green-500/20 p-4">
          <div className="flex space-x-3">
            {/* Search Input with integrated icons */}
            <div className="flex-1 relative">
              <input
                type="text"
                value={inputText + (interimTranscript ? ' ' + interimTranscript : '')}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && !isLoading && sendMessage()}
                placeholder="Type your message..."
                disabled={isLoading}
                className="w-full px-4 py-3 pr-20 bg-gray-700 border border-green-500/30 rounded-lg text-green-300 placeholder-green-500/50 focus:outline-none focus:ring-2 focus:ring-green-400 focus:border-green-400 transition-all disabled:opacity-50"
              />
              
              {/* Upload and Send icons inside input */}
              <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center space-x-1">
                <button
                  onClick={toggleListening}
                  disabled={isLoading}
                  className={`p-1.5 ${isListening ? 'text-red-400' : 'text-green-400'} hover:bg-green-400/10 rounded transition-all disabled:opacity-50`}
                  title={isListening ? "Stop Listening" : "Start Voice Input"}
                >
                  {isListening ? <MicOff className="w-4 h-4 animate-pulse" /> : <Mic className="w-4 h-4" />}
                </button>

                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={(e) => handleFileUpload(e.target.files)}
                  multiple
                  accept="*/*"
                  className="hidden"
                />
                
                <button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isLoading}
                  className="p-1.5 text-green-400 hover:text-green-300 hover:bg-green-400/10 rounded transition-all disabled:opacity-50"
                  title="Upload Files"
                >
                  <Upload className="w-4 h-4" />
                </button>
                
                <button
                  onClick={sendMessage}
                  disabled={isLoading || (!inputText.trim() && uploadedFiles.length === 0)}
                  className="p-1.5 text-green-400 hover:text-green-300 hover:bg-green-400/10 rounded transition-all disabled:opacity-50"
                  title="Send Message"
                >
                  {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Summarize Button */}
            <button
              onClick={summarizeFiles}
              disabled={uploadedFiles.length === 0 || isLoading}
              className={`px-6 py-3 rounded-lg flex items-center space-x-2 transition-all font-bold ${
                uploadedFiles.length > 0 && !isLoading
                  ? 'bg-gradient-to-r from-green-500 to-green-600 text-black hover:from-green-400 hover:to-green-500 shadow-lg shadow-green-500/20'
                  : 'bg-gray-700 text-gray-500 cursor-not-allowed border border-gray-600'
              }`}
            >
              <FileText className="w-4 h-4" />
              <span>Summarize</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatComponent;