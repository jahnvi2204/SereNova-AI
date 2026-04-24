import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Heart, MessageSquare, Shield, BrainCircuit, Sparkles, ArrowRight, User, Send } from "lucide-react";
import Navbar from "./Navbar"; 
import { chatAPI, authAPI } from '../api/api';

const HomePage = () => {
  const navigate = useNavigate();
  const [loaded, setLoaded] = useState(false);
  const [currentTestimonial, setCurrentTestimonial] = useState(0);
  const [previewMessage, setPreviewMessage] = useState('');
  const [previewChat, setPreviewChat] = useState([
    { text: "Hello! I'm SeraNova, your personal mental health companion. How are you feeling today?", isUser: false }
  ]);
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);
  
  // Redirect logged-in users to chat page
  useEffect(() => {
    if (authAPI.isAuthenticated()) {
      navigate('/chat');
    }
  }, [navigate]);
  
  const testimonials = [
    {
      quote: "SeraNova has become my daily companion for managing anxiety. It's like having a therapist in my pocket.",
      author: "Sarah M."
    },
    {
      quote: "The guided meditations and personalized exercises have made such a difference in my mental well-being.",
      author: "Michael L."
    },
    {
      quote: "As someone who struggles with opening up, SeraNova provided the perfect space to explore my thoughts.",
      author: "Jamie K."
    }
  ];
  
  useEffect(() => {
    setLoaded(true);
    
    const testimonialInterval = setInterval(() => {
      setCurrentTestimonial((prev) => (prev + 1) % testimonials.length);
    }, 6000);
    
    return () => clearInterval(testimonialInterval);
  }, [testimonials.length]);

  const handlePreviewSubmit = async (e) => {
    if (e) e.preventDefault();
    if (!previewMessage.trim()) return;

    // Add user message
    setPreviewChat(prev => [...prev, { text: previewMessage, isUser: true }]);
    const currentMessage = previewMessage;
    setPreviewMessage('');
    setIsPreviewLoading(true);

    try {
      const responseData = await chatAPI.sendMessagePublic(currentMessage.trim());

      setPreviewChat(prev => [...prev, { 
        text: responseData.response, 
        isUser: false, 
        intent: responseData.intent 
      }]);
    } catch (error) {
      console.error('Error:', error);
      setPreviewChat(prev => [...prev, { 
        text: "Sorry, I'm having trouble connecting. Try the full chat interface!", 
        isUser: false 
      }]);
    } finally {
      setIsPreviewLoading(false);
    }
  };

  const benefits = [
    {
      icon: <Heart className="h-6 w-6 text-theme-highlight" />,
      title: "Compassionate Support",
      description: "Experience empathetic conversation designed to provide emotional relief and understanding"
    },
    {
      icon: <BrainCircuit className="h-6 w-6 text-theme-highlight" />,
      title: "AI-Powered Insights",
      description: "Receive personalized therapeutic guidance based on your unique emotional patterns"
    },
    {
      icon: <Shield className="h-6 w-6 text-theme-highlight" />,
      title: "Private & Secure",
      description: "Your conversations are confidential and protected with advanced encryption"
    },
    {
      icon: <MessageSquare className="h-6 w-6 text-theme-highlight" />,
      title: "Available 24/7",
      description: "Access support whenever you need it, day or night, without waiting for appointments"
    }
  ];

  return (
    <div className="min-h-screen bg-theme-background flex flex-col relative overflow-hidden">
      {/* Animated Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-theme-accent/20 to-theme-highlight/10 animate-gradient-x"></div>

      {/* Include the Navbar component */}
      <Navbar />

      <main className="flex-grow container mx-auto px-4 pt-24 pb-12 z-10 flex flex-col items-center justify-center">
        <div className="w-full max-w-6xl">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            {/* Left Side - Hero Content */}
            <div className={`transform transition-all duration-1000 ${loaded ? 'translate-x-0 opacity-100' : '-translate-x-12 opacity-0'}`}>
              <div className="flex items-center mb-4">
                <div className="relative">
                  <Heart className="h-8 w-8 text-theme-highlight" />
                  <span className="absolute -top-1 -right-1">
                    <Sparkles className="h-4 w-4 text-yellow-400" />
                  </span>
                </div>
                <h1 className="text-3xl font-bold ml-3 text-theme-primary-text">SeraNova AI</h1>
              </div>
              
              <h2 className="text-4xl md:text-5xl font-bold text-theme-primary-text mt-6 mb-6 leading-tight">
                Your Personal <span className="text-theme-highlight">Mental Health</span> Companion
              </h2>
              
              <p className="text-xl text-theme-primary-text mb-8 max-w-xl">
                Experience compassionate AI-powered therapy that adapts to your unique emotional needs. Begin your journey toward better mental wellbeing today.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 mt-8">
                <a href="/chat">
                  <button  className="relative group bg-theme-highlight hover:bg-theme-highlight/90 text-theme-background px-8 py-4 rounded-lg text-lg font-semibold transition-all duration-300 transform hover:scale-105 flex items-center justify-center space-x-3 hover:shadow-lg hover:shadow-theme-highlight/30 overflow-hidden">
                    {/* Button Shine Effect */}
                    <div className="absolute inset-0 opacity-0 group-hover:opacity-30 transition-opacity duration-500 bg-gradient-to-r from-white/30 via-white/10 to-white/30 w-[200%] animate-shine"></div>
                    
                    <span className="relative z-10">Start Your Session</span>
                    <ArrowRight className="ml-2 h-5 w-5 relative z-10" />
                  </button>
                </a>
                
                <a href="#learn-more">
                  <button className="px-8 py-4 rounded-lg text-lg font-semibold transition-all duration-300 border border-theme-accent text-theme-highlight hover:bg-theme-accent hover:text-theme-primary-text">
                    Learn How It Works
                  </button>
                </a>
              </div>
              
              <div className="mt-12">
                <div className="flex items-center space-x-4 mb-2">
                  <div className="flex -space-x-2">
                    <div className="w-8 h-8 rounded-full bg-theme-accent flex items-center justify-center text-xs font-medium text-theme-primary-text shadow-lg">SM</div>
                    <div className="w-8 h-8 rounded-full bg-theme-highlight flex items-center justify-center text-xs font-medium text-theme-background shadow-lg">ML</div>
                    <div className="w-8 h-8 rounded-full bg-theme-accent/80 flex items-center justify-center text-xs font-medium text-theme-primary-text shadow-lg">JK</div>
                    <div className="w-8 h-8 rounded-full bg-theme-accent/50 flex items-center justify-center text-xs font-medium text-theme-primary-text shadow-lg">
                      <span>+</span>
                    </div>
                  </div>
                  <p className="text-theme-secondary-text text-sm">Join thousands finding peace of mind</p>
                </div>
              </div>
            </div>
            
            {/* Right Side - Preview */}
            <div className={`transform transition-all duration-1000 delay-300 ${loaded ? 'translate-x-0 opacity-100' : 'translate-x-12 opacity-0'}`}>
              <div className="relative">
                {/* Glowing effects */}
                <div className="absolute -top-10 -right-10 w-32 h-32 bg-theme-highlight/20 rounded-full blur-xl animate-float"></div>
                <div className="absolute -bottom-10 -left-10 w-32 h-32 bg-theme-accent/20 rounded-full blur-xl animate-float-delayed"></div>
                
                <div className="bg-theme-surface/90 backdrop-blur-lg rounded-2xl border border-theme-accent/50 shadow-xl overflow-hidden w-full max-w-md mx-auto">
                  {/* Chat preview header */}
                  <div className="p-4 bg-theme-surface border-b border-theme-accent flex items-center">
                    <div className="flex items-center space-x-2">
                      <div className="relative">
                        <Heart className="h-6 w-6 text-theme-highlight" />
                        <span className="absolute -top-1 -right-1">
                          <Sparkles className="h-3 w-3 text-yellow-400" />
                        </span>
                      </div>
                      <h3 className="text-lg font-medium text-theme-primary-text">SeraNova Assistant</h3>
                    </div>
                    <div className="ml-auto flex items-center space-x-1">
                      <span className="inline-block w-2 h-2 bg-green-400 rounded-full"></span>
                      <span className="text-xs text-green-400">Online</span>
                    </div>
                  </div>
                  
                  {/* Chat preview content */}
                  <div className="p-5 h-80 flex flex-col bg-gradient-to-b from-theme-surface to-theme-background">
                    <div className="flex-1 overflow-y-auto space-y-4 mb-4">
                      {previewChat.map((message, index) => (
                        <div key={index} className={`flex items-start ${message.isUser ? 'justify-end' : ''}`}>
                          {!message.isUser && (
                            <div className="flex-shrink-0 bg-theme-highlight rounded-full p-2">
                              <MessageSquare className="h-4 w-4 text-theme-background" />
                            </div>
                          )}
                          <div className={`ml-3 ${message.isUser ? 'mr-3 ml-0' : ''} rounded-lg py-2 px-3 text-sm max-w-xs ${
                            message.isUser ? 'bg-theme-accent/30 text-theme-primary-text' : 'bg-theme-surface text-theme-primary-text'
                          }`}>
                            <p className="text-theme-primary-text">{message.text}</p>
                          </div>
                          {message.isUser && (
                            <div className="flex-shrink-0 bg-theme-accent rounded-full p-2">
                              <User className="h-4 w-4 text-theme-primary-text" />
                            </div>
                          )}
                        </div>
                      ))}
                      
                      {/* Loading indicator */}
                          {isPreviewLoading && (
                        <div className="flex items-start">
                          <div className="flex-shrink-0 bg-theme-highlight rounded-full p-2">
                            <MessageSquare className="h-4 w-4 text-theme-background" />
                          </div>
                          <div className="ml-3 bg-theme-surface rounded-lg py-2 px-3 text-sm max-w-xs text-theme-primary-text">
                            <div className="flex space-x-1">
                              <div className="w-2 h-2 rounded-full bg-theme-highlight animate-bounce"></div>
                              <div className="w-2 h-2 rounded-full bg-theme-highlight animate-bounce delay-75"></div>
                              <div className="w-2 h-2 rounded-full bg-theme-highlight animate-bounce delay-150"></div>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                    
                    {/* Chat input */}
                    <div className="mt-auto">
                      <form onSubmit={handlePreviewSubmit} className="relative">
                        <input
                          type="text"
                          value={previewMessage}
                          onChange={(e) => setPreviewMessage(e.target.value)}
                          placeholder="Share what's on your mind..."
                          className="w-full bg-theme-surface border border-theme-accent rounded-lg py-3 pl-4 pr-10 text-theme-primary-text placeholder:text-theme-secondary-text focus:outline-none focus:ring-2 focus:ring-theme-highlight"
                          style={{ color: '#E0E6F3' }}
                          disabled={isPreviewLoading}
                        />
                        <button 
                          type="submit"
                          disabled={isPreviewLoading || !previewMessage.trim()}
                          className="absolute right-2 top-2 text-theme-highlight p-1 rounded-full hover:bg-theme-accent disabled:opacity-50"
                        >
                          <Send className="h-5 w-5" />
                        </button>
                      </form>
                      <p className="text-xs text-theme-secondary-text mt-2 text-center">
                        Try me out! For the full experience, <a href="/chat" className="text-theme-highlight hover:text-theme-highlight/80">start a session</a>
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Benefits Section */}
          <div id="learn-more" className={`mt-24 transform transition-all duration-1000 delay-500 ${loaded ? 'translate-y-0 opacity-100' : 'translate-y-12 opacity-0'}`}>
            <h3 className="text-2xl font-bold text-center text-theme-primary-text mb-12">How SeraNova Helps Your Mental Wellbeing</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {benefits.map((benefit, index) => (
                <div 
                  key={index} 
                  className="bg-theme-surface/50 backdrop-blur-sm border border-theme-accent/50 rounded-xl p-6 transition-all duration-300 hover:transform hover:scale-105 hover:bg-theme-surface/80 hover:border-theme-highlight/30"
                >
                  <div className="bg-theme-accent/30 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                    {benefit.icon}
                  </div>
                  <h4 className="text-lg font-semibold text-theme-primary-text mb-2">{benefit.title}</h4>
                  <p className="text-theme-primary-text text-sm">{benefit.description}</p>
                </div>
              ))}
            </div>
          </div>
          
          {/* Testimonial Section */}
          <div className={`mt-24 mb-12 transform transition-all duration-1000 delay-700 ${loaded ? 'translate-y-0 opacity-100' : 'translate-y-12 opacity-0'}`}>
            <div className="max-w-3xl mx-auto bg-gradient-to-br from-theme-accent/20 to-theme-surface/20 backdrop-blur-md rounded-2xl p-8 border border-theme-accent/30">
              <div className="relative">
                <svg className="absolute top-0 left-0 w-10 h-10 text-theme-highlight/50 transform -translate-x-6 -translate-y-6" fill="currentColor" viewBox="0 0 32 32">
                  <path d="M9.352 4C4.456 7.456 1 13.12 1 19.36c0 5.088 3.072 8.064 6.624 8.064 3.36 0 5.856-2.688 5.856-5.856 0-3.168-2.208-5.472-5.088-5.472-.576 0-1.344.096-1.536.192.48-3.264 3.552-7.104 6.624-9.024L9.352 4zm16.512 0c-4.8 3.456-8.256 9.12-8.256 15.36 0 5.088 3.072 8.064 6.624 8.064 3.264 0 5.856-2.688 5.856-5.856 0-3.168-2.304-5.472-5.184-5.472-.576 0-1.248.096-1.44.192.48-3.264 3.456-7.104 6.528-9.024L25.864 4z"></path>
                </svg>
                
                <div className="relative h-32">
                  {testimonials.map((testimonial, index) => (
                    <div 
                      key={index} 
                      className={`absolute inset-0 transition-all duration-1000 ease-in-out ${
                        currentTestimonial === index 
                          ? 'opacity-100 translate-x-0' 
                          : 'opacity-0 translate-x-12'
                      }`}
                    >
                      <p className="text-theme-primary-text text-lg italic">{testimonial.quote}</p>
                      <p className="text-theme-highlight font-medium mt-4">— {testimonial.author}</p>
                    </div>
                  ))}
                </div>
                
                <div className="flex justify-center mt-6 space-x-2">
                  {testimonials.map((_, index) => (
                    <button 
                      key={index}
                      onClick={() => setCurrentTestimonial(index)}
                      className={`w-2 h-2 rounded-full transition-all duration-300 ${
                        currentTestimonial === index ? 'bg-theme-highlight w-6' : 'bg-theme-accent'
                      }`}
                      aria-label={`View testimonial ${index + 1}`}
                    ></button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
      
      {/* Footer */}
      <footer className="relative z-10 border-t border-theme-accent py-8 bg-theme-surface/80 backdrop-blur-sm">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center mb-4 md:mb-0">
              <Heart className="h-6 w-6 text-theme-highlight mr-2" />
              <span className="text-theme-primary-text font-medium">SeraNova AI</span>
            </div>
            
            <div className="text-theme-secondary-text text-sm">
              © {new Date().getFullYear()} SeraNova AI. All rights reserved.
            </div>
            
            <div className="flex space-x-6 mt-4 md:mt-0">
              <button onClick={() => {}} className="text-theme-secondary-text hover:text-theme-highlight transition-colors cursor-pointer">Privacy</button>
              <button onClick={() => {}} className="text-theme-secondary-text hover:text-theme-highlight transition-colors cursor-pointer">Terms</button>
              <button onClick={() => {}} className="text-theme-secondary-text hover:text-theme-highlight transition-colors cursor-pointer">Support</button>
            </div>
          </div>
        </div>
      </footer>

      {/* Add custom animations in CSS */}
      <style>{`
        @keyframes gradient-x {
          0% { background-position: 0% 50% }
          50% { background-position: 100% 50% }
          100% { background-position: 0% 50% }
        }
        @keyframes shine {
          from { transform: translateX(-100%) }
          to { transform: translateX(100%) }
        }
        @keyframes float {
          0%, 100% { transform: translateY(0) }
          50% { transform: translateY(-10px) }
        }
        @keyframes pulse {
          0%, 100% { opacity: 1 }
          50% { opacity: 0.5 }
        }
        .animate-gradient-x {
          background-size: 200% 200%;
          animation: gradient-x 15s ease infinite;
        }
        .animate-shine {
          animation: shine 2s infinite;
        }
        .animate-float {
          animation: float 4s ease-in-out infinite;
        }
        .animate-float-delayed {
          animation: float 5s ease-in-out infinite 1s;
        }
        .animate-pulse-slow {
          animation: pulse 3s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
};

export default HomePage;