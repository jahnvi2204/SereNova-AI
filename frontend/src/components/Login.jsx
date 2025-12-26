import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, EyeOff, MessageSquare, ChevronRight, Lock, Mail, Sparkles, Heart, Bot, Shield, BrainCircuit } from 'lucide-react';
import { authAPI } from '../api/api';

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [formError, setFormError] = useState('');
  
  // Animation states
  const [animateForm, setAnimateForm] = useState(false);
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0);
  
  const demoMessages = [
    "How are you feeling today?",
    "I'm here to listen whenever you need me",
    "Your mental wellbeing is important",
    "Let's explore your thoughts together"
  ];

  useEffect(() => {
    // Trigger entrance animation
    setAnimateForm(true);
    
    // Simple message rotation without typing effect
    const messageInterval = setInterval(() => {
      setCurrentMessageIndex((prev) => (prev + 1) % demoMessages.length);
    }, 4000);
    
    return () => clearInterval(messageInterval);
  }, [demoMessages.length]);

  const handleSubmit = async () => {
    setFormError('');
    
    if (!email || !password) {
      setFormError('Please fill in all fields');
      return;
    }

    setIsLoading(true);
    
    try {
      const response = await authAPI.login({ email, password });
      console.log('Login successful:', response);
      setIsLoading(false);
      // Redirect to chat page after successful login
      navigate('/chat');
    } catch (error) {
      console.error('Login error:', error);
      setFormError(error.message || 'Login failed. Please try again.');
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-theme-background text-theme-primary-text">
      {/* Left side: Login form */}
      <div className="w-full md:w-1/2 flex flex-col justify-center p-8">
        <div 
          className={`max-w-md mx-auto w-full transition-all duration-700 transform ${
            animateForm ? 'translate-y-0 opacity-100' : 'translate-y-8 opacity-0'
          }`}
        >
          <div className="flex items-center mb-8">
            <div className="relative">
              <Heart className="h-10 w-10 text-theme-highlight" />
              <span className="absolute -top-1 -right-1">
                <Sparkles className="h-5 w-5 text-yellow-400" />
              </span>
            </div>
            <h1 className="text-3xl font-bold ml-3">SeraNova AI</h1>
          </div>
          
          <h2 className="text-2xl font-semibold mb-2">Welcome back</h2>
          <p className="text-theme-secondary-text mb-6">Your personal mental health companion</p>
          
          {formError && (
            <div className="bg-red-900/30 border border-red-500 text-red-300 px-4 py-3 rounded mb-4">
              {formError}
            </div>
          )}
          
          <div className="space-y-5">
            <div className="space-y-2">
              <label htmlFor="email" className="block text-sm font-medium text-theme-secondary-text">Email address</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-theme-secondary-text" />
                </div>
                <input
                  id="email"
                  name="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="bg-theme-surface block w-full pl-10 pr-3 py-3 border border-theme-accent rounded-lg focus:ring-2 focus:ring-theme-highlight focus:border-theme-highlight transition-all duration-200 text-theme-primary-text placeholder:text-theme-secondary-text"
                  placeholder="your.email@example.com"
                  style={{ color: '#E0E6F3' }}
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label htmlFor="password" className="block text-sm font-medium text-theme-secondary-text">Password</label>
                <div className="text-sm text-theme-highlight-400 hover:text-theme-highlight-300 transition-colors cursor-pointer">
                  Forgot password?
                </div>
              </div>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-theme-secondary-text" />
                </div>
                <input
                  id="password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="bg-theme-surface block w-full pl-10 pr-10 py-3 border border-theme-accent rounded-lg focus:ring-2 focus:ring-theme-highlight focus:border-theme-highlight transition-all duration-200"
                  placeholder="••••••••"
                />
                <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="text-theme-secondary-text hover:text-theme-secondary-text focus:outline-none"
                  >
                    {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                  </button>
                </div>
              </div>
            </div>
            
            <div className="flex items-center">
              <input
                id="remember-me"
                name="remember-me"
                type="checkbox"
                className="h-4 w-4 bg-theme-surface border-theme-accent rounded text-theme-highlight focus:ring-theme-highlight"
              />
              <label htmlFor="remember-me" className="ml-2 block text-sm text-theme-secondary-text">
                Remember me for 30 days
              </label>
            </div>
            
            <button
              onClick={handleSubmit}
              disabled={isLoading}
              className={`w-full flex justify-center items-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-theme-primary-text bg-theme-highlight hover:bg-theme-highlight focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-theme-highlight transition-colors ${
                isLoading ? 'opacity-80 cursor-wait' : ''
              }`}
            >
              {isLoading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-theme-primary-text" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Connecting...
                </>
              ) : (
                <>
                  Sign In
                  <ChevronRight className="ml-2 h-5 w-5" />
                </>
              )}
            </button>
          </div>
          
          <div className="mt-8">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-theme-accent"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-theme-background text-theme-secondary-text">New to SeraNova?</span>
              </div>
            </div>
            
            <button className="mt-6 w-full flex justify-center py-2 px-4 border border-theme-accent text-theme-highlight rounded-lg shadow-sm bg-transparent hover:bg-theme-accent/30 transition-colors duration-200"
            onClick={() => navigate('/signup')}>
              Create an account
            </button>
          </div>
        </div>
      </div>
      
      {/* Right side: Preview */}
      <div className="hidden md:flex md:w-1/2 bg-theme-surface relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-theme-accent/30 to-theme-highlight/20"></div>
        
        <div className="relative w-full h-full flex flex-col justify-center items-center p-12">
          <div className="w-full max-w-md bg-theme-background/70 backdrop-blur-sm rounded-xl overflow-hidden shadow-xl border border-theme-accent">
            <div className="p-4 bg-theme-surface flex items-center border-b border-theme-accent">
              <Bot className="h-6 w-6 text-theme-highlight-400 mr-2" />
              <h3 className="text-lg font-medium">SeraNova Therapy Assistant</h3>
            </div>
            
            <div className="p-5 h-72 flex flex-col">
              <div className="flex-1 overflow-y-auto space-y-4">
                <div className="flex items-start">
                  <div className="flex-shrink-0 bg-theme-highlight rounded-full p-2">
                    <Bot className="h-5 w-5 text-theme-primary-text" />
                  </div>
                  <div className="ml-3 bg-theme-surface rounded-lg py-2 px-3 text-sm">
                    Hello again! I'm your mental health companion. How can I support you today?
                  </div>
                </div>
                
                <div className="flex items-start">
                  <div className="flex-shrink-0 bg-theme-highlight rounded-full p-2">
                    <Bot className="h-5 w-5 text-theme-primary-text" />
                  </div>
                  <div className="ml-3 bg-theme-surface rounded-lg py-2 px-3 text-sm">
                    {demoMessages[currentMessageIndex]}
                  </div>
                </div>
              </div>
              
              <div className="mt-4 relative">
                <input
                  type="text"
                  placeholder="Share what's on your mind..."
                  className="w-full bg-theme-surface border border-theme-accent rounded-lg py-2 pl-4 pr-10 focus:outline-none focus:ring-2 focus:ring-theme-highlight"
                  disabled
                />
                <button className="absolute right-2 top-2 text-theme-highlight-400 p-1 rounded-full hover:bg-theme-accent">
                  <MessageSquare className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
          
          <div className="mt-12 text-center">
            <h2 className="text-2xl font-bold mb-4">Your Mental Wellness Partner</h2>
            <p className="text-theme-secondary-text max-w-sm">
              SeraNova AI uses advanced emotional intelligence to provide personalized support for your mental health journey.
            </p>
            
            <div className="mt-8 grid grid-cols-3 gap-4 max-w-md">
              <div className="p-4 bg-theme-surface/80 backdrop-blur-sm rounded-lg border border-theme-accent">
                <div className="text-theme-highlight-400 mb-2">
                  <Heart className="h-8 w-8 mx-auto" />
                </div>
                <p className="text-sm">Compassionate care</p>
              </div>
              
              <div className="p-4 bg-theme-surface/80 backdrop-blur-sm rounded-lg border border-theme-accent">
                <div className="text-theme-highlight-400 mb-2">
                  <Shield className="h-8 w-8 mx-auto" />
                </div>
                <p className="text-sm">Private & secure</p>
              </div>
              
              <div className="p-4 bg-theme-surface/80 backdrop-blur-sm rounded-lg border border-theme-accent">
                <div className="text-theme-highlight-400 mb-2">
                  <BrainCircuit className="h-8 w-8 mx-auto" />
                </div>
                <p className="text-sm">Personalized insights</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;