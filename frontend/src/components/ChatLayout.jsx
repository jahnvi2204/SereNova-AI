import React, { useState, useRef, useEffect } from 'react';
import { 
  FiMessageSquare, 
  FiSettings, 
  FiUser, 
  FiLogOut, 
  FiSend,
  FiPlus,
  FiChevronLeft,
  FiMenu,
  FiX,
  FiTrash2,
  FiXCircle
} from 'react-icons/fi';
import { chatAPI, authAPI } from '../api/api';
import Navbar from './Navbar';

const ChatLayout = () => {
  const [message, setMessage] = useState('');
  const [conversation, setConversation] = useState([
    { id: `greeting-initial`, text: "Hi there! How can I help you today?", isUser: false, intent: "greeting" },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [conversations, setConversations] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [user, setUser] = useState(null);
  const [hasUpdatedTitle, setHasUpdatedTitle] = useState(false);
  const [contextMenu, setContextMenu] = useState({ visible: false, x: 0, y: 0, chatId: null });
  const [showSettings, setShowSettings] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const messageEndRef = useRef(null);
  const inputRef = useRef(null);
  
  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation]);
  
  // Initialize user and sessions on component mount
  useEffect(() => {
    const initializeChat = async () => {
      try {
        // Check if user is authenticated
        if (!authAPI.isAuthenticated()) {
          window.location.href = '/login';
          return;
        }

        // Get user data
        const userData = authAPI.getCurrentUser();
        setUser(userData);

        // Load existing sessions
        const sessionsData = await chatAPI.getSessions();
        const sessionsList = sessionsData.sessions || [];
        
        // Mark the first session as active or create a new one
        if (sessionsList.length > 0) {
          const updatedSessions = sessionsList.map((session, index) => ({
            ...session,
            active: index === 0
          }));
          setConversations(updatedSessions);
          setCurrentSessionId(sessionsList[0].id);
          
          // Load messages for the first session
          await loadSessionMessages(sessionsList[0].id);
        } else {
          // Create a new session if none exist
          await createNewSession();
        }
      } catch (error) {
        console.error('Failed to initialize chat:', error);
        // If token is invalid, redirect to login
        if (error.message.includes('Authentication')) {
          window.location.href = '/login';
        }
      }
    };

    initializeChat();
    inputRef.current?.focus();
  }, []);

  // Load messages for a specific session
  const loadSessionMessages = async (sessionId) => {
    try {
      const messagesData = await chatAPI.getSessionMessages(sessionId);
      const messages = messagesData.messages || [];
      
      if (messages.length === 0) {
        // If no messages, start with greeting
        setConversation([
          { id: `greeting-${Date.now()}`, text: "Hi there! How can I help you today?", isUser: false, intent: "greeting" }
        ]);
      } else {
        // Transform database messages (which have 'message' and 'response') into conversation format
        const conversationMessages = [];
        messages.forEach((msg, idx) => {
          // Add user message
          if (msg.message) {
            conversationMessages.push({
              id: `user-${msg.id || idx}-${Date.now()}`,
              text: msg.message,
              isUser: true
            });
          }
          // Add AI response
          if (msg.response) {
            conversationMessages.push({
              id: `bot-${msg.id || idx}-${Date.now()}`,
              text: msg.response,
              isUser: false,
              intent: msg.intent || null
            });
          }
        });
        setConversation(conversationMessages);
      }
    } catch (error) {
      console.error('Failed to load session messages:', error);
      setConversation([
        { id: `greeting-error-${Date.now()}`, text: "Hi there! How can I help you today?", isUser: false, intent: "greeting" }
      ]);
    }
  };

  // Create a new chat session
  const createNewSession = async () => {
    try {
      const newSession = await chatAPI.createSession();
      const sessionWithActiveFlag = {
        ...newSession.session,
        active: true
      };
      
      // Update conversations list
      setConversations(prev => [
        sessionWithActiveFlag,
        ...prev.map(c => ({ ...c, active: false }))
      ]);
      
      setCurrentSessionId(newSession.session.id);
      setHasUpdatedTitle(false); // Reset flag for new session
      setConversation([
        { id: `greeting-new-session-${Date.now()}`, text: "Hi there! How can I help you today?", isUser: false, intent: "greeting" }
      ]);
    } catch (error) {
      console.error('Failed to create new session:', error);
    }
  };

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    if (!message.trim()) return;
  
    // Add user message immediately with unique ID
    const userMessageId = `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    setConversation(prev => [
      ...prev,
      { id: userMessageId, text: message, isUser: true }
    ]);
    
    const currentMessage = message;
    setMessage('');
    setIsLoading(true);
    
    try {
      // Use the session messages endpoint which saves messages and updates title automatically
      const response = await fetch(`${process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000'}/chat/sessions/${currentSessionId}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify({ message: currentMessage.trim() }),
      });
      
      const responseData = await response.json();
      
      if (!response.ok) {
        throw new Error(responseData.error || 'Failed to send message');
      }
      
      const botMessageId = `bot-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      setConversation(prev => [
        ...prev,
        { 
          id: botMessageId,
          text: responseData.response, 
          isUser: false, 
          intent: responseData.intent 
        }
      ]);
      
      // Update session title if this is the first message and we got an intent
      if (!hasUpdatedTitle && responseData.intent && currentSessionId) {
        const title = responseData.intent.replace("_", " ").replace(/\b\w/g, l => l.toUpperCase());
        try {
          await chatAPI.updateSession(currentSessionId, { title });
          // Update the conversations list with new title
          setConversations(prev => 
            prev.map(c => 
              c.id === currentSessionId 
                ? { ...c, title: title }
                : c
            )
          );
          setHasUpdatedTitle(true);
        } catch (updateError) {
          console.error('Failed to update session title:', updateError);
        }
      }
    } catch (error) {
      console.error('Error:', error);
      const errorMessageId = `error-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      setConversation(prev => [
        ...prev,
        { 
          id: errorMessageId,
          text: "Sorry, I'm having trouble connecting to the server.", 
          isUser: false 
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // This function is no longer needed as we're using the backend API

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const startNewChat = async () => {
    await createNewSession();
  };

  const selectChat = async (id) => {
    setConversations(prev => 
      prev.map(c => ({ 
        ...c, 
        active: c.id === id 
      }))
    );
    setCurrentSessionId(id);
    await loadSessionMessages(id);
  };

  const handleLogout = async () => {
    try {
      await authAPI.logout();
      window.location.href = '/';
    } catch (error) {
      console.error('Logout error:', error);
      // Force logout even if API call fails
      window.location.href = '/';
    }
  };

  // Handle right-click on chat item
  const handleChatRightClick = (e, chatId) => {
    e.preventDefault();
    e.stopPropagation();
    
    // Calculate position to prevent menu from going off-screen
    const menuWidth = 150;
    const menuHeight = 50;
    const x = e.clientX + menuWidth > window.innerWidth 
      ? window.innerWidth - menuWidth - 10 
      : e.clientX;
    const y = e.clientY + menuHeight > window.innerHeight 
      ? window.innerHeight - menuHeight - 10 
      : e.clientY;
    
    setContextMenu({
      visible: true,
      x: x,
      y: y,
      chatId: chatId
    });
  };

  // Close context menu
  const closeContextMenu = () => {
    setContextMenu({ visible: false, x: 0, y: 0, chatId: null });
  };

  // Delete chat session
  const handleDeleteChat = async (chatId) => {
    const chatTitle = conversations.find(c => c.id === chatId)?.title || 'this chat';
    if (!window.confirm(`Are you sure you want to delete "${chatTitle}"? This action cannot be undone.`)) {
      closeContextMenu();
      return;
    }
    
    try {
      await chatAPI.deleteSession(chatId);
      // Remove from conversations list
      setConversations(prev => prev.filter(c => c.id !== chatId));
      
      // If deleted chat was active, switch to another or create new
      if (currentSessionId === chatId) {
        const remainingChats = conversations.filter(c => c.id !== chatId);
        if (remainingChats.length > 0) {
          await selectChat(remainingChats[0].id);
        } else {
          await createNewSession();
        }
      }
      
      closeContextMenu();
    } catch (error) {
      console.error('Failed to delete chat:', error);
      alert('Failed to delete chat. Please try again.');
      closeContextMenu();
    }
  };

  // Close context menu when clicking outside
  useEffect(() => {
    const handleClickOutside = () => {
      if (contextMenu.visible) {
        closeContextMenu();
      }
    };
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [contextMenu.visible]);
  
  // Determine if user is typing a longer message
  const isLongMessage = message.length > 50;

  return (
    <div className="flex flex-col h-screen bg-theme-background">
      {/* Navbar */}
      <Navbar />
      
      <div className="flex flex-1 overflow-hidden pt-16">
      {/* Mobile sidebar toggle */}
      <button 
        onClick={toggleSidebar} 
        className="md:hidden fixed z-20 bottom-5 left-5 bg-theme-highlight text-theme-primary-text p-3 rounded-full shadow-lg"
      >
        {sidebarOpen ? <FiX /> : <FiMenu />}
      </button>
      
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} 
                       md:translate-x-0 transition-transform duration-300 ease-in-out 
                       fixed md:static w-72 h-full z-10 bg-theme-background shadow-lg p-4 flex flex-col`}>
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-2">
            <FiMessageSquare className="text-theme-primary-text text-xl" />
            <h1 className="text-xl text-theme-primary-text font-bold">SereNova AI</h1>
          </div>
          <button 
            onClick={toggleSidebar} 
            className="md:hidden text-theme-primary-text"
            aria-label="Close sidebar"
          >
            <FiChevronLeft size={20} />
          </button>
        </div>
        
        {/* New chat button */}
        <button 
          onClick={startNewChat}
          className="flex items-center gap-2 mb-4 w-full p-3 bg-theme-surface hover:bg-theme-highlight text-theme-primary-text rounded-lg transition"
        >
          <FiPlus />
          <span>New Chat</span>
        </button>

        {/* Conversations list */}
        <div className="mb-6">
          <h2 className="text-xs uppercase text-theme-primary-text font-semibold mb-2 tracking-wider">Recent Chats</h2>
          <div className="space-y-1">
            {conversations.map((chat) => (
              <button
                key={chat.id}
                onClick={() => selectChat(chat.id)}
                onContextMenu={(e) => handleChatRightClick(e, chat.id)}
                className={`w-full text-left p-3 rounded-lg transition text-sm flex items-center gap-2 ${
                  chat.active 
                    ? 'bg-theme-highlight text-theme-primary-text font-medium hover:bg-theme-highlight' 
                    : 'text-theme-primary-text hover:bg-theme-accent/30'
                }`}
              >
                <FiMessageSquare size={16} />
                <span className="truncate text-theme-primary-text">{chat.title}</span>
              </button>
            ))}
          </div>
          
          {/* Context Menu */}
          {contextMenu.visible && (
            <div
              className="fixed bg-theme-surface border border-theme-accent rounded-lg shadow-lg z-50 py-2 min-w-[150px]"
              style={{
                left: `${contextMenu.x}px`,
                top: `${contextMenu.y}px`,
              }}
              onClick={(e) => e.stopPropagation()}
              onContextMenu={(e) => e.preventDefault()}
            >
              <button
                onClick={() => handleDeleteChat(contextMenu.chatId)}
                className="w-full text-left px-4 py-2 text-sm text-red-500 hover:bg-red-500/10 flex items-center gap-2 transition"
              >
                <FiTrash2 size={16} />
                <span>Delete Chat</span>
              </button>
            </div>
          )}
        </div>

        <nav className="flex-1 space-y-1">
          <button 
            onClick={() => setShowSettings(true)}
            className="flex items-center gap-3 p-3 text-theme-primary-text hover:bg-theme-accent rounded-lg transition w-full text-left"
          >
            <FiSettings size={18} />
            <span>Settings</span>
          </button>
          <button 
            onClick={() => setShowProfile(true)}
            className="flex items-center gap-3 p-3 text-theme-primary-text hover:bg-theme-accent rounded-lg transition w-full text-left"
          >
            <FiUser size={18} />
            <span>Profile</span>
          </button>
        </nav>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 bg-theme-surface flex flex-col">
        {/* Chat header */}
        <div className="p-4 bg-theme-surface border-b border-theme-accent">
          <h2 className="font-bold text-lg text-theme-primary-text font-serif"> 
            {conversations.find(c => c.active)?.title || "Chat"}
          </h2>
        </div>
        
        <div className="flex-1 flex flex-col p-6 overflow-hidden">
          <div className="flex-1 bg-theme-background rounded-xl shadow-md overflow-hidden flex flex-col">
            
            {/* Messages container */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {conversation.map((entry, index) => (
                <div 
                  key={entry.id || `msg-${index}-${entry.text?.substring(0, 10)}-${entry.isUser}`} 
                  className={`flex ${entry.isUser ? 'justify-end' : 'justify-start'} animate-fadeIn`}
                >
                  {!entry.isUser && (
                    <div className="w-8 h-8 rounded-full bg-theme-highlight/20 flex items-center justify-center mr-2 mt-1 flex-shrink-0">
                      <FiMessageSquare className="text-theme-highlight" />
                    </div>
                  )}
                  
                  <div 
                    className={`max-w-[75%] p-4 rounded-2xl ${
                      entry.isUser 
                        ? 'bg-theme-highlight text-theme-background rounded-tr-none' 
                        : 'bg-theme-surface rounded-tl-none text-theme-primary-text'
                    }`}
                  >
                    <p className="leading-relaxed text-theme-primary-text">{entry.text}</p>
                    {!entry.isUser && entry.intent && (
                      <span className="inline-block text-xs mt-2 opacity-70 px-2 py-1 rounded-full bg-theme-accent/30 text-theme-primary-text">
                        {entry.intent}
                      </span>
                    )}
                  </div>
                  
                  {entry.isUser && (
                    <div className="w-8 h-8 rounded-full bg-theme-highlight flex items-center justify-center ml-2 mt-1 flex-shrink-0">
                      <FiUser className="text-theme-primary-text" />
                    </div>
                  )}
                </div>
              ))}
              
              {/* Loading indicator */}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="w-8 h-8 rounded-full bg-theme-highlight/20 flex items-center justify-center mr-2 mt-1 flex-shrink-0">
                    <FiMessageSquare className="text-theme-highlight" />
                  </div>
                  <div className="max-w-[70%] p-4 rounded-2xl bg-theme-surface rounded-tl-none">
                    <div className="flex space-x-2">
                      <div className="w-2 h-2 rounded-full bg-theme-highlight animate-bounce"></div>
                      <div className="w-2 h-2 rounded-full bg-theme-highlight animate-bounce delay-75"></div>
                      <div className="w-2 h-2 rounded-full bg-theme-highlight animate-bounce delay-150"></div>
                    </div>
                  </div>
                </div>
              )}
              
              {/* Auto-scroll anchor */}
              <div ref={messageEndRef} />
            </div>

            {/* Input area */}
            <div className="border-t border-theme-accent100 p-4">
              <div className="flex items-end gap-2">
                <div className="flex-1 relative">
                  <textarea
                    ref={inputRef}
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Type your message..."
                    disabled={isLoading}
                    rows={isLongMessage ? 3 : 1}
                    className="w-full p-4 pr-10 border border-theme-accent rounded-xl focus:outline-none focus:ring-2 focus:ring-theme-highlight disabled:bg-theme-surface resize-none transition-all text-theme-primary-text placeholder:text-theme-secondary-text bg-theme-surface"
                    style={{ color: '#E0E6F3' }}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSubmit();
                      }
                    }}
                  />
                  <div className="absolute bottom-3 right-3 text-theme-secondary-text text-xs">
                    {message.length > 0 && `${message.length} chars`}
                  </div>
                </div>
                
                <button
                  onClick={handleSubmit}
                  disabled={isLoading || !message.trim()}
                  className={`p-4 rounded-xl text-theme-primary-text ${
                    isLoading || !message.trim() 
                      ? 'bg-theme-accent cursor-not-allowed' 
                      : 'bg-theme-highlight hover:bg-theme-highlight'
                  } transition-colors flex-shrink-0`}
                >
                  <FiSend size={18} />
                </button>
              </div>
              
              <div className="mt-2 text-xs text-theme-secondary-text px-1">
                Press Enter to send, Shift+Enter for a new line
              </div>
            </div>
          </div>
        </div>
      </div>
      </div>

      {/* Settings Modal */}
      {showSettings && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setShowSettings(false)}>
          <div className="bg-theme-background rounded-xl shadow-2xl p-6 w-full max-w-md mx-4" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-theme-primary-text">Settings</h2>
              <button
                onClick={() => setShowSettings(false)}
                className="text-theme-secondary-text hover:text-theme-primary-text transition"
              >
                <FiXCircle size={24} />
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="p-4 bg-theme-surface rounded-lg">
                <h3 className="text-theme-primary-text font-semibold mb-2">Appearance</h3>
                <p className="text-theme-secondary-text text-sm">Theme settings coming soon</p>
              </div>
              
              <div className="p-4 bg-theme-surface rounded-lg">
                <h3 className="text-theme-primary-text font-semibold mb-2">Notifications</h3>
                <p className="text-theme-secondary-text text-sm">Notification preferences coming soon</p>
              </div>
              
              <div className="p-4 bg-theme-surface rounded-lg">
                <h3 className="text-theme-primary-text font-semibold mb-2">Privacy</h3>
                <p className="text-theme-secondary-text text-sm">Privacy settings coming soon</p>
              </div>
              
              <div className="p-4 bg-theme-surface rounded-lg">
                <h3 className="text-theme-primary-text font-semibold mb-2">About</h3>
                <p className="text-theme-secondary-text text-sm">SereNova AI v1.0.0</p>
                <p className="text-theme-secondary-text text-sm">Your Personal Mental Health Companion</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Profile Modal */}
      {showProfile && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setShowProfile(false)}>
          <div className="bg-theme-background rounded-xl shadow-2xl p-6 w-full max-w-md mx-4" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-theme-primary-text">Profile</h2>
              <button
                onClick={() => setShowProfile(false)}
                className="text-theme-secondary-text hover:text-theme-primary-text transition"
              >
                <FiXCircle size={24} />
              </button>
            </div>
            
            {user ? (
              <div className="space-y-6">
                <div className="flex items-center justify-center mb-6">
                  <div className="w-24 h-24 rounded-full bg-theme-highlight flex items-center justify-center">
                    <FiUser size={48} className="text-theme-primary-text" />
                  </div>
                </div>
                
                {/* Username and Email Display at Top */}
                <div className="text-center mb-6 pb-4 border-b border-theme-accent">
                  <h3 className="text-xl font-bold text-theme-primary-text">
                    {user.full_name || user.name || user.fullName || 'User'}
                  </h3>
                  <p className="text-theme-secondary-text text-sm mt-1">
                    {user.email || 'No email set'}
                  </p>
                </div>
                
                <div className="space-y-4">
                  <div className="p-4 bg-theme-surface rounded-lg">
                    <label className="text-xs uppercase text-theme-secondary-text font-semibold tracking-wider mb-2 block">
                      Full Name
                    </label>
                    <p className="text-theme-primary-text text-lg font-medium">
                      {user.full_name || user.name || user.fullName || 'Not set'}
                    </p>
                  </div>
                  
                  <div className="p-4 bg-theme-surface rounded-lg">
                    <label className="text-xs uppercase text-theme-secondary-text font-semibold tracking-wider mb-2 block">
                      Email Address
                    </label>
                    <p className="text-theme-primary-text text-lg font-medium">
                      {user.email || 'Not set'}
                    </p>
                  </div>
                  
                  <div className="p-4 bg-theme-surface rounded-lg">
                    <label className="text-xs uppercase text-theme-secondary-text font-semibold tracking-wider mb-2 block">
                      Account Created
                    </label>
                    <p className="text-theme-primary-text text-sm">
                      {user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                    </p>
                  </div>
                </div>
                
                {/* Logout Button */}
                <div className="pt-4 border-t border-theme-accent">
                  <button
                    onClick={async () => {
                      await handleLogout();
                      setShowProfile(false);
                    }}
                    className="w-full flex items-center justify-center gap-3 p-3 text-red-500 hover:bg-red-500/10 rounded-lg transition"
                  >
                    <FiLogOut size={18} />
                    <span>Logout</span>
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-theme-secondary-text">User information not available</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatLayout;