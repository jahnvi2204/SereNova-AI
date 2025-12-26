// Connection test utility for React-Flask integration
import { testConnection } from '../api/api';

/**
 * Test backend connection and log status
 */
export const checkBackendConnection = async () => {
  try {
    const result = await testConnection();
    if (result.connected) {
      console.log('✅ Backend connected:', result.message);
      console.log('📊 Status:', result.status);
      console.log('💾 Database:', result.database);
      return true;
    } else {
      console.error('❌ Backend connection failed:', result.error);
      return false;
    }
  } catch (error) {
    console.error('❌ Backend connection error:', error.message);
    return false;
  }
};

/**
 * Initialize connection check on app load
 */
export const initConnectionCheck = () => {
  // Check connection after a short delay to ensure app is loaded
  setTimeout(() => {
    checkBackendConnection();
  }, 1000);
};

