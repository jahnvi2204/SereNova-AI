// API utility functions for SeraNova AI
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';
// API_TIMEOUT can be used for future timeout implementations
// const API_TIMEOUT = parseInt(process.env.REACT_APP_API_TIMEOUT) || 10000;
const TOKEN_STORAGE_KEY = process.env.REACT_APP_TOKEN_STORAGE_KEY || 'authToken';
const USER_DATA_STORAGE_KEY = process.env.REACT_APP_USER_DATA_STORAGE_KEY || 'userData';

// Helper function to get auth token from localStorage
const getAuthToken = () => {
  return localStorage.getItem(TOKEN_STORAGE_KEY);
};

// Helper function to create headers with auth token
const getAuthHeaders = () => {
  const token = getAuthToken();
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };
};

// Helper function to handle API responses
const handleResponse = async (response) => {
  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch (e) {
      // If response is not JSON, use status text
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }
    throw new Error(errorData.error || `API request failed: ${response.status}`);
  }
  return await response.json();
};

// Test backend connection
export const testConnection = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    const data = await response.json();
    return {
      connected: response.ok,
      status: data.status,
      database: data.database,
      message: data.message || 'Backend is reachable'
    };
  } catch (error) {
    return {
      connected: false,
      error: error.message || 'Cannot connect to backend server'
    };
  }
};

// Authentication API calls
export const authAPI = {
  // User signup
  signup: async (userData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });
      
      const data = await handleResponse(response);
      
      // Store token and user data
      if (data.token) {
        localStorage.setItem(TOKEN_STORAGE_KEY, data.token);
        localStorage.setItem(USER_DATA_STORAGE_KEY, JSON.stringify(data.user));
      }
      
      return data;
    } catch (error) {
      console.error('Signup error:', error);
      throw error;
    }
  },

  // User login
  login: async (credentials) => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });
      
      const data = await handleResponse(response);
      
      // Store token and user data
      if (data.token) {
        localStorage.setItem(TOKEN_STORAGE_KEY, data.token);
        localStorage.setItem(USER_DATA_STORAGE_KEY, JSON.stringify(data.user));
      }
      
      return data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },

  // User logout
  logout: async () => {
    try {
      const token = getAuthToken();
      if (token) {
        await fetch(`${API_BASE_URL}/auth/logout`, {
          method: 'POST',
          headers: getAuthHeaders(),
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear local storage regardless of API call success
      localStorage.removeItem(TOKEN_STORAGE_KEY);
      localStorage.removeItem(USER_DATA_STORAGE_KEY);
    }
  },

  // Verify token
  verifyToken: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/verify`, {
        method: 'GET',
        headers: getAuthHeaders(),
      });
      
      return await handleResponse(response);
    } catch (error) {
      console.error('Token verification error:', error);
      // Clear invalid token
      localStorage.removeItem(TOKEN_STORAGE_KEY);
      localStorage.removeItem(USER_DATA_STORAGE_KEY);
      throw error;
    }
  },

  // Get current user data from localStorage
  getCurrentUser: () => {
    try {
      const userData = localStorage.getItem(USER_DATA_STORAGE_KEY);
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      console.error('Error getting user data:', error);
      return null;
    }
  },

  // Check if user is authenticated
  isAuthenticated: () => {
    return !!getAuthToken();
  }
};

// Chat API calls
export const chatAPI = {
  // Send message to chatbot
  sendMessage: async (message, sessionId = null) => {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/predict`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          message,
          session_id: sessionId
        }),
      });
      
      return await handleResponse(response);
    } catch (error) {
      console.error('Send message error:', error);
      throw error;
    }
  },

  // Send message to public endpoint (no auth required)
  sendMessagePublic: async (message) => {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/predict-public`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      });
      
      return await handleResponse(response);
    } catch (error) {
      console.error('Send public message error:', error);
      throw error;
    }
  },

  // Get chat sessions
  getSessions: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/sessions`, {
        method: 'GET',
        headers: getAuthHeaders(),
      });
      
      return await handleResponse(response);
    } catch (error) {
      console.error('Get sessions error:', error);
      throw error;
    }
  },

  // Create new chat session
  createSession: async (title = 'New Chat') => {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/sessions`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ title }),
      });
      
      return await handleResponse(response);
    } catch (error) {
      console.error('Create session error:', error);
      throw error;
    }
  },

  // Get messages for a session
  getSessionMessages: async (sessionId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}/messages`, {
        method: 'GET',
        headers: getAuthHeaders(),
      });
      
      return await handleResponse(response);
    } catch (error) {
      console.error('Get session messages error:', error);
      throw error;
    }
  },

  // Update chat session (e.g., title)
  updateSession: async (sessionId, updates) => {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}`, {
        method: 'PATCH',
        headers: getAuthHeaders(),
        body: JSON.stringify(updates),
      });
      
      return await handleResponse(response);
    } catch (error) {
      console.error('Update session error:', error);
      throw error;
    }
  },

  // Delete chat session
  deleteSession: async (sessionId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      });
      
      return await handleResponse(response);
    } catch (error) {
      console.error('Delete session error:', error);
      throw error;
    }
  },

  // Get Spotify playlist recommendations based on mood
  getPlaylists: async (mood) => {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/playlists`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ mood }),
      });
      
      return await handleResponse(response);
    } catch (error) {
      console.error('Get playlists error:', error);
      throw error;
    }
  }
};

// Export default API object
const api = {
  auth: authAPI,
  chat: chatAPI
};

export default api;
