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
      // Use centralized API helper for session message flow
      const responseData = await chatAPI.addSessionMessage(currentSessionId, currentMessage.trim());
      
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
    <div className="app-mesh flex h-screen max-h-screen flex-col overflow-hidden">
      <div className="mesh-grid pointer-events-none" />
      <Navbar />

      <div className="relative z-10 flex min-h-0 flex-1 flex-row overflow-hidden pt-24">
      <button
        type="button"
        onClick={toggleSidebar}
        className="fixed bottom-5 left-5 z-20 flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/10 text-zinc-100 shadow-glow backdrop-blur-xl md:hidden"
        aria-label="Toggle sidebar"
      >
        {sidebarOpen ? <FiX /> : <FiMenu />}
      </button>

      <div
        className={`${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } fixed z-30 flex h-full w-72 max-w-[85vw] flex-col border-r border-white/[0.08] bg-zinc-950/80 p-4 shadow-glow-sm backdrop-blur-2xl transition-transform duration-300 ease-out md:static md:translate-x-0`}
      >
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-400/20 to-indigo-500/20 ring-1 ring-white/10" />
            <h1 className="text-sm font-semibold tracking-tight text-zinc-100">SereNova</h1>
          </div>
          <button
            type="button"
            onClick={toggleSidebar}
            className="text-zinc-400 md:hidden"
            aria-label="Close sidebar"
          >
            <FiChevronLeft size={20} />
          </button>
        </div>

        <button
          type="button"
          onClick={startNewChat}
          className="mb-4 flex w-full items-center justify-center gap-2 rounded-2xl border border-white/10 bg-white/[0.04] py-3 text-sm font-medium text-zinc-100 transition hover:border-white/20 hover:bg-white/[0.08]"
        >
          <FiPlus />
          <span>New session</span>
        </button>

        <div className="mb-6 min-h-0 flex-1 overflow-y-auto pr-0.5">
          <h2 className="mb-2 text-[10px] font-semibold uppercase tracking-[0.2em] text-zinc-500">Sessions</h2>
          <div className="space-y-1">
            {conversations.map((chat) => (
              <button
                key={chat.id}
                type="button"
                onClick={() => selectChat(chat.id)}
                onContextMenu={(e) => handleChatRightClick(e, chat.id)}
                className={`flex w-full items-center gap-2 rounded-xl p-3 text-left text-sm transition ${
                  chat.active
                    ? 'bg-white/[0.1] font-medium text-white ring-1 ring-white/10'
                    : 'text-zinc-400 hover:bg-white/[0.05] hover:text-zinc-200'
                }`}
              >
                <FiMessageSquare size={16} className="shrink-0 opacity-60" />
                <span className="truncate">{chat.title || 'Chat'}</span>
              </button>
            ))}
          </div>
          
          {/* Context Menu */}
          {contextMenu.visible && (
            <div
              className="fixed z-50 min-w-[150px] rounded-xl border border-white/10 bg-zinc-950/95 py-2 shadow-2xl backdrop-blur-xl"
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

        <nav className="mt-auto space-y-1 border-t border-white/[0.06] pt-4">
          <button
            type="button"
            onClick={() => setShowSettings(true)}
            className="flex w-full items-center gap-3 rounded-xl p-3 text-left text-sm text-zinc-400 transition hover:bg-white/[0.05] hover:text-zinc-200"
          >
            <FiSettings size={18} />
            <span>Settings</span>
          </button>
          <button
            type="button"
            onClick={() => setShowProfile(true)}
            className="flex w-full items-center gap-3 rounded-xl p-3 text-left text-sm text-zinc-400 transition hover:bg-white/[0.05] hover:text-zinc-200"
          >
            <FiUser size={18} />
            <span>Profile</span>
          </button>
        </nav>
      </div>

      <div className="flex min-h-0 min-w-0 flex-1 flex-col bg-transparent">
        <div className="border-b border-white/[0.08] bg-black/20 px-5 py-4 backdrop-blur-xl">
          <h2 className="text-sm font-medium tracking-tight text-zinc-100">
            {conversations.find((c) => c.active)?.title || 'Session'}
          </h2>
        </div>

        <div className="flex min-h-0 flex-1 flex-col overflow-hidden p-4 sm:p-6">
          <div className="glass flex min-h-0 flex-1 flex-col overflow-hidden p-0">
            
            {/* Messages container */}
            <div className="flex-1 space-y-4 overflow-y-auto p-5 sm:p-6">
              {conversation.map((entry, index) => (
                <div
                  key={entry.id || `msg-${index}-${entry.text?.substring(0, 10)}-${entry.isUser}`}
                  className={`flex ${entry.isUser ? 'justify-end' : 'justify-start'}`}
                >
                  {!entry.isUser && (
                    <div className="mr-2 mt-0.5 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-xl bg-white/[0.06] ring-1 ring-white/10">
                      <FiMessageSquare className="text-zinc-300" />
                    </div>
                  )}

                  <div
                    className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                      entry.isUser
                        ? 'bg-white text-zinc-900'
                        : 'border border-white/[0.08] bg-white/[0.04] text-zinc-200'
                    }`}
                  >
                    <p className="whitespace-pre-wrap text-sm leading-relaxed">{entry.text}</p>
                    {!entry.isUser && entry.intent && (
                      <span className="mt-2 inline-block rounded-full border border-white/10 bg-white/[0.04] px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider text-zinc-500">
                        {entry.intent}
                      </span>
                    )}
                  </div>

                  {entry.isUser && (
                    <div className="ml-2 mt-0.5 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-xl bg-zinc-700/90">
                      <FiUser className="text-zinc-200" />
                    </div>
                  )}
                </div>
              ))}
              
              {/* Loading indicator */}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="mr-2 mt-0.5 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-xl bg-white/[0.06]">
                    <FiMessageSquare className="text-zinc-400" />
                  </div>
                  <div className="max-w-[70%] rounded-2xl border border-white/[0.08] bg-white/[0.04] px-4 py-3">
                    <div className="flex gap-1.5">
                      <div className="h-1.5 w-1.5 animate-bounce rounded-full bg-zinc-500" />
                      <div className="h-1.5 w-1.5 animate-bounce rounded-full bg-zinc-500 [animation-delay:0.1s]" />
                      <div className="h-1.5 w-1.5 animate-bounce rounded-full bg-zinc-500 [animation-delay:0.2s]" />
                    </div>
                  </div>
                </div>
              )}
              
              {/* Auto-scroll anchor */}
              <div ref={messageEndRef} />
            </div>

            {/* Input area */}
            <div className="border-t border-white/[0.08] p-4 sm:p-5">
              <div className="flex items-end gap-2">
                <div className="relative flex-1">
                  <textarea
                    ref={inputRef}
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Message…"
                    disabled={isLoading}
                    rows={isLongMessage ? 3 : 1}
                    className="w-full resize-none rounded-2xl border border-white/10 bg-black/30 px-4 py-3.5 pr-12 text-sm text-zinc-100 placeholder:text-zinc-600 focus:border-white/20 focus:outline-none focus:ring-1 focus:ring-white/10 disabled:opacity-50"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSubmit();
                      }
                    }}
                  />
                  <div className="absolute bottom-3 right-3 text-xs text-zinc-600">
                    {message.length > 0 ? `${message.length}` : ''}
                  </div>
                </div>

                <button
                  type="button"
                  onClick={handleSubmit}
                  disabled={isLoading || !message.trim()}
                  className={`flex h-[52px] w-[52px] flex-shrink-0 items-center justify-center rounded-2xl text-zinc-950 transition ${
                    isLoading || !message.trim()
                      ? 'cursor-not-allowed bg-zinc-800 text-zinc-600'
                      : 'bg-white hover:bg-zinc-100'
                  }`}
                >
                  <FiSend size={18} />
                </button>
              </div>
              <p className="mt-2 text-[11px] text-zinc-600">Enter to send · Shift+Enter for newline</p>
            </div>
          </div>
        </div>
      </div>
      </div>

      {/* Settings Modal */}
      {showSettings && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={() => setShowSettings(false)}>
          <div className="glass mx-4 w-full max-w-md p-6" onClick={(e) => e.stopPropagation()}>
            <div className="mb-6 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-zinc-100">Settings</h2>
              <button
                type="button"
                onClick={() => setShowSettings(false)}
                className="text-zinc-500 transition hover:text-zinc-200"
              >
                <FiXCircle size={22} />
              </button>
            </div>

            <div className="space-y-3 text-sm text-zinc-500">
              <div className="glass-tight p-4">
                <h3 className="mb-1 font-medium text-zinc-200">Appearance</h3>
                <p>Coming soon.</p>
              </div>
              <div className="glass-tight p-4">
                <h3 className="mb-1 font-medium text-zinc-200">Notifications</h3>
                <p>Coming soon.</p>
              </div>
              <div className="glass-tight p-4">
                <h3 className="mb-1 font-medium text-zinc-200">Privacy</h3>
                <p>Coming soon.</p>
              </div>
              <div className="glass-tight p-4">
                <h3 className="mb-1 font-medium text-zinc-200">About</h3>
                <p className="text-zinc-400">SereNova · v1.0.0</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Profile Modal */}
      {showProfile && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={() => setShowProfile(false)}>
          <div className="glass mx-4 w-full max-w-md p-6" onClick={(e) => e.stopPropagation()}>
            <div className="mb-6 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-zinc-100">Profile</h2>
              <button
                type="button"
                onClick={() => setShowProfile(false)}
                className="text-zinc-500 transition hover:text-zinc-200"
              >
                <FiXCircle size={22} />
              </button>
            </div>

            {user ? (
              <div className="space-y-5">
                <div className="mb-2 flex items-center justify-center">
                  <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-white/[0.08] ring-1 ring-white/10">
                    <FiUser size={36} className="text-zinc-200" />
                  </div>
                </div>

                <div className="mb-4 border-b border-white/[0.08] pb-4 text-center">
                  <h3 className="text-lg font-semibold text-zinc-100">
                    {user.full_name || user.name || user.fullName || 'User'}
                  </h3>
                  <p className="mt-1 text-sm text-zinc-500">
                    {user.email || 'No email set'}
                  </p>
                </div>

                <div className="space-y-3 text-sm">
                  <div className="glass-tight p-3">
                    <p className="text-[10px] font-semibold uppercase tracking-wider text-zinc-500">Name</p>
                    <p className="mt-1 text-zinc-200">{user.full_name || user.name || user.fullName || 'Not set'}</p>
                  </div>
                  <div className="glass-tight p-3">
                    <p className="text-[10px] font-semibold uppercase tracking-wider text-zinc-500">Email</p>
                    <p className="mt-1 text-zinc-200">{user.email || 'Not set'}</p>
                  </div>
                  <div className="glass-tight p-3">
                    <p className="text-[10px] font-semibold uppercase tracking-wider text-zinc-500">Created</p>
                    <p className="mt-1 text-zinc-400">
                      {user.created_at ? new Date(user.created_at).toLocaleDateString() : '—'}
                    </p>
                  </div>
                </div>

                <div className="border-t border-white/[0.08] pt-4">
                  <button
                    type="button"
                    onClick={async () => {
                      await handleLogout();
                      setShowProfile(false);
                    }}
                    className="flex w-full items-center justify-center gap-2 rounded-xl border border-red-500/20 py-2.5 text-sm text-red-400 transition hover:bg-red-500/10"
                  >
                    <FiLogOut size={18} />
                    Log out
                  </button>
                </div>
              </div>
            ) : (
              <div className="py-8 text-center text-sm text-zinc-500">No user data</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatLayout;