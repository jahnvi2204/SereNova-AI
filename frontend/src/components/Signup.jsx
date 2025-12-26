import { useState, useEffect } from 'react';
import { Eye, EyeOff, Check, ChevronRight, ArrowRight, Lock, Mail, Sparkles, Heart, User } from 'lucide-react';
import { authAPI } from '../api/api';

const Signup = () => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [formError, setFormError] = useState('');
  const [registrationComplete, setRegistrationComplete] = useState(false);
  const [acceptTerms, setAcceptTerms] = useState(false);
  
  // Animation states
  const [animateForm, setAnimateForm] = useState(false);
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0);
  
  const demoMessages = [
    "Join thousands finding peace of mind",
    "Sign up for personalized mental wellness support",
    "Your journey to better mental health starts here",
    "Create an account for confidential support"
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
    
    if (!fullName || !email || !password || !confirmPassword) {
      setFormError('Please fill in all fields');
      return;
    }
    
    if (password !== confirmPassword) {
      setFormError('Passwords do not match');
      return;
    }
    
    if (!acceptTerms) {
      setFormError('Please accept the terms and privacy policy');
      return;
    }

    // Password validation
    if (password.length < 8) {
      setFormError('Password must be at least 8 characters long');
      return;
    }

    setIsLoading(true);
    
    try {
      const response = await authAPI.signup({
        fullName,
        email,
        password
      });
      console.log('Signup successful:', response);
      setRegistrationComplete(true);
    } catch (error) {
      console.error('Signup error:', error);
      setFormError(error.message || 'Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Password strength indicator
  const getPasswordStrength = () => {
    if (!password) return { strength: 0, label: "" };
    
    let strength = 0;
    if (password.length >= 8) strength += 1;
    if (/[A-Z]/.test(password)) strength += 1;
    if (/[0-9]/.test(password)) strength += 1;
    if (/[^A-Za-z0-9]/.test(password)) strength += 1;
    
    const labels = ["Weak", "Fair", "Good", "Strong"];
    
    return {
      strength,
      label: labels[strength - 1] || ""
    };
  };
  
  const passwordStrength = getPasswordStrength();

  // Show success screen after registration
  if (registrationComplete) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-theme-background text-theme-primary-text p-6">
        <div className="bg-theme-surface rounded-lg p-8 w-full max-w-md border border-theme-accent shadow-lg transform transition-all duration-500 scale-100">
          <div className="flex flex-col items-center space-y-6">
            <div className="w-20 h-20 bg-theme-highlight rounded-full flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-theme-primary-text" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold">Account Created!</h2>
            <p className="text-theme-secondary-text text-center">Welcome to SeraNova AI, {fullName}</p>
            
            <div className="mt-6 w-full">
              <div className="repository-preview bg-theme-accent rounded-lg p-4 mb-4 hover:bg-theme-accent transition duration-300">
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="font-medium text-theme-highlight">SeraNova-AI</h3>
                    <p className="text-sm text-theme-secondary-text">Your personal therapeutic assistant</p>
                  </div>
                  <Heart className="h-5 w-5 text-theme-highlight" />
                </div>
              </div>
              
              <button 
                className="w-full bg-theme-highlight hover:bg-theme-highlight transition-colors duration-300 text-theme-primary-text py-3 rounded-lg mt-6 flex items-center justify-center"
                onClick={() => window.location.href = '/chat'}
              >
                <span>Start Your First Session</span>
                <ArrowRight className="ml-2 h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-theme-background text-theme-primary-text">
      {/* Left side: Sign up form */}
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
          
          <h2 className="text-2xl font-semibold mb-2">Create your account</h2>
          <p className="text-theme-secondary-text mb-6">Join SeraNova for personalized mental health support</p>
          
          {formError && (
            <div className="bg-red-900/30 border border-red-500 text-red-300 px-4 py-3 rounded mb-4">
              {formError}
            </div>
          )}
          
          <div className="space-y-5">
            <div className="space-y-2">
              <label htmlFor="fullName" className="block text-sm font-medium text-theme-secondary-text">Full Name</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-5 w-5 text-theme-secondary-text" />
                </div>
                <input
                  id="fullName"
                  name="fullName"
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="bg-theme-surface block w-full pl-10 pr-3 py-3 border border-theme-accent rounded-lg focus:ring-2 focus:ring-theme-highlight focus:border-theme-highlight transition-all duration-200 text-theme-primary-text placeholder:text-theme-secondary-text"
                  placeholder="Your full name"
                  style={{ color: '#E0E6F3' }}
                />
              </div>
            </div>
            
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
              <label htmlFor="password" className="block text-sm font-medium text-theme-secondary-text">Password</label>
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
                  className="bg-theme-surface block w-full pl-10 pr-10 py-3 border border-theme-accent rounded-lg focus:ring-2 focus:ring-theme-highlight focus:border-theme-highlight transition-all duration-200 text-theme-primary-text placeholder:text-theme-secondary-text"
                  placeholder="Create a strong password"
                  style={{ color: '#E0E6F3' }}
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
              {password && (
                <div className="mt-2">
                  <div className="flex items-center justify-between mb-1">
                    <div className="text-xs text-theme-secondary-text">Password strength:</div>
                    <div className={`text-xs ${
                      passwordStrength.strength === 0 ? 'text-theme-secondary-text' :
                      passwordStrength.strength === 1 ? 'text-red-400' :
                      passwordStrength.strength === 2 ? 'text-yellow-400' :
                      passwordStrength.strength === 3 ? 'text-green-400' :
                      'text-green-300'
                    }`}>{passwordStrength.label}</div>
                  </div>
                  <div className="w-full bg-theme-accent rounded-full h-1.5">
                    <div className={`h-1.5 rounded-full ${
                      passwordStrength.strength === 0 ? 'bg-theme-accent w-0' :
                      passwordStrength.strength === 1 ? 'bg-red-500 w-1/4' :
                      passwordStrength.strength === 2 ? 'bg-yellow-500 w-2/4' :
                      passwordStrength.strength === 3 ? 'bg-green-500 w-3/4' :
                      'bg-green-400 w-full'
                    }`}></div>
                  </div>
                </div>
              )}
            </div>
            
            <div className="space-y-2">
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-theme-secondary-text">Confirm Password</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-theme-secondary-text" />
                </div>
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type={showConfirmPassword ? "text" : "password"}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="bg-theme-surface block w-full pl-10 pr-10 py-3 border border-theme-accent rounded-lg focus:ring-2 focus:ring-theme-highlight focus:border-theme-highlight transition-all duration-200 text-theme-primary-text placeholder:text-theme-secondary-text"
                  placeholder="Confirm your password"
                  style={{ color: '#E0E6F3' }}
                />
                <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="text-theme-secondary-text hover:text-theme-secondary-text focus:outline-none"
                  >
                    {showConfirmPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                  </button>
                </div>
              </div>
              {confirmPassword && password === confirmPassword && (
                <div className="flex items-center text-green-400 text-xs mt-1">
                  <Check className="h-4 w-4 mr-1" />
                  Passwords match
                </div>
              )}
            </div>
            
            <div className="flex items-start">
              <div className="flex items-center h-5">
                <input
                  id="terms"
                  name="terms"
                  type="checkbox"
                  checked={acceptTerms}
                  onChange={(e) => setAcceptTerms(e.target.checked)}
                  className="h-4 w-4 bg-theme-surface border-theme-accent rounded text-theme-highlight focus:ring-theme-highlight"
                />
              </div>
              <div className="ml-3 text-sm">
                <label htmlFor="terms" className="text-theme-secondary-text">
                  I agree to the <span className="text-theme-highlight cursor-pointer">Terms of Service</span> and <span className="text-theme-highlight cursor-pointer">Privacy Policy</span>
                </label>
              </div>
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
                  Creating Account...
                </>
              ) : (
                <>
                  Create Account
                  <ChevronRight className="ml-2 h-5 w-5" />
                </>
              )}
            </button>
          </div>
          
          <div className="mt-8 text-center">
            <div className="text-sm">
              <span className="text-theme-secondary-text">Already have an account?</span>
              <a  href="/login" className="ml-1 text-theme-highlight hover:text-theme-highlight-300 transition-colors cursor-pointer">
                Sign in
               
              </a>
            </div>
          </div>
        </div>
      </div>
      
      {/* Right side: Preview */}
      <div className="hidden md:flex md:w-1/2 bg-theme-surface relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-theme-highlight-900/50 to-blue-900/50"></div>
        
        <div className="relative w-full h-full flex flex-col justify-center items-center p-12">
          <div className="w-full max-w-md bg-theme-background/70 backdrop-blur-sm rounded-xl overflow-hidden shadow-xl border border-theme-accent">
            <div className="p-5">
              <h3 className="text-xl font-medium mb-4">Why join SeraNova AI?</h3>
              <div className="space-y-4 mb-6">
                <div className="flex items-start">
                  <div className="flex-shrink-0 bg-theme-highlight/20 rounded-full p-1">
                    <Check className="h-5 w-5 text-theme-highlight" />
                  </div>
                  <div className="ml-3 text-sm text-theme-secondary-text">
                    <span className="font-medium text-theme-primary-text">24/7 Support</span> - Access therapeutic guidance whenever you need it
                  </div>
                </div>
                
                <div className="flex items-start">
                  <div className="flex-shrink-0 bg-theme-highlight/20 rounded-full p-1">
                    <Check className="h-5 w-5 text-theme-highlight" />
                  </div>
                  <div className="ml-3 text-sm text-theme-secondary-text">
                    <span className="font-medium text-theme-primary-text">Personalized Experience</span> - AI that adapts to your unique needs and progress
                  </div>
                </div>
                
                <div className="flex items-start">
                  <div className="flex-shrink-0 bg-theme-highlight/20 rounded-full p-1">
                    <Check className="h-5 w-5 text-theme-highlight" />
                  </div>
                  <div className="ml-3 text-sm text-theme-secondary-text">
                    <span className="font-medium text-theme-primary-text">Privacy Focused</span> - Confidential conversations in a secure environment
                  </div>
                </div>
                
                <div className="flex items-start">
                  <div className="flex-shrink-0 bg-theme-highlight/20 rounded-full p-1">
                    <Check className="h-5 w-5 text-theme-highlight" />
                  </div>
                  <div className="ml-3 text-sm text-theme-secondary-text">
                    <span className="font-medium text-theme-primary-text">Evidence-Based Techniques</span> - Grounded in proven therapeutic approaches
                  </div>
                </div>
              </div>
              
              <div className="bg-theme-surface/80 p-4 rounded-lg border border-theme-accent">
                <p className="text-sm text-theme-secondary-text italic">"{demoMessages[currentMessageIndex]}"</p>
              </div>
            </div>
          </div>
          
          <div className="mt-12 text-center max-w-md">
            <div className="flex justify-center space-x-8 mb-8">
              <div className="text-center">
                <div className="text-3xl font-bold text-theme-highlight">24/7</div>
                <p className="text-sm text-theme-secondary-text mt-1">Always available</p>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold text-theme-highlight">100%</div>
                <p className="text-sm text-theme-secondary-text mt-1">Confidential</p>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold text-theme-highlight">10k+</div>
                <p className="text-sm text-theme-secondary-text mt-1">Users helped</p>
              </div>
            </div>
            
            <div className="flex items-center justify-center space-x-4">
              <div className="flex -space-x-2">
                <div className="w-8 h-8 rounded-full bg-theme-highlight flex items-center justify-center text-xs font-medium">JD</div>
                <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-xs font-medium">SK</div>
                <div className="w-8 h-8 rounded-full bg-green-600 flex items-center justify-center text-xs font-medium">AP</div>
                <div className="w-8 h-8 rounded-full bg-yellow-600 flex items-center justify-center text-xs font-medium">TM</div>
              </div>
              <div className="text-sm text-theme-secondary-text">Join thousands on their mental wellness journey</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Signup