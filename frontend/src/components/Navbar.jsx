import React, { useState, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { Heart, MessageSquare, Sparkles, HomeIcon, Music, LogIn } from "lucide-react";
import PlaylistModal from "./PlaylistModal";
import { authAPI } from '../api/api';


const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [isScrolled, setIsScrolled] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [showPlaylistModal, setShowPlaylistModal] = useState(false);
  
  // Check if we're on the home page
  const isHomePage = location.pathname === '/';
  
  // Handle home click - redirect to chat if logged in
  const handleHomeClick = (e) => {
    if (authAPI.isAuthenticated()) {
      e.preventDefault();
      navigate('/chat');
    }
  };

  // Add a scroll event listener to detect scrolling
  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 50) {
        setIsScrolled(true);
      } else {
        setIsScrolled(false);
      }
    };

    window.addEventListener("scroll", handleScroll);

    // Cleanup the event listener on component unmount
    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, []);

  return (
    <>
      {/* Top Navbar */}
      <nav
        className={`fixed top-0 left-0 w-full z-50 backdrop-blur-sm shadow-lg transition-all duration-300 ${
          isScrolled ? "bg-theme-background/90" : "bg-theme-background/60"
        }`}
      >
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-center h-16">
            {/* Left-aligned logo */}
            <div className="flex items-center">
              <div className="relative">
                <Heart className="h-6 w-6 text-theme-highlight" />
                <span className="absolute -top-1 -right-1">
                  <Sparkles className="h-3 w-3 text-yellow-400" />
                </span>
              </div>
              <span className="ml-2 text-xl font-bold text-theme-primary-text">SeraNova AI</span>
            </div>

            {/* Center-aligned navigation items */}
            <ul className="hidden md:flex space-x-7 text-lg justify-start font-semibold">
              <li>
                <Link
                  to="/"
                  onClick={handleHomeClick}
                  className="text-theme-primary-text hover:text-theme-highlight transition duration-300 flex items-center space-x-2"
                >
                  <HomeIcon className="h-4 w-4" />
                  <span>Home</span>
                </Link>
              </li>
              <li>
                <Link
                  to="/chat"
                  className="text-theme-primary-text hover:text-theme-highlight transition duration-300 flex items-center space-x-2"
                >
                  <MessageSquare className="h-4 w-4" />
                  <span>Chat</span>
                </Link>
              </li>
              <li>
                <button
                  onClick={(e) => { e.preventDefault(); setShowPlaylistModal(true); }}
                  className="text-theme-primary-text hover:text-theme-highlight transition duration-300 flex items-center space-x-2"
                >
                  <Music className="h-4 w-4" />
                  <span>Playlist</span>
                </button>
              </li>
            </ul>

            {/* Right-aligned section (e.g., login button) */}
            <div className="flex items-center space-x-6">
              {/* Only show Login button on home page */}
              {isHomePage && (
                <Link
                  to="/login"
                  className="text-theme-primary-text hover:text-theme-highlight transition duration-300 flex items-center space-x-2"
                >
                  <LogIn className="h-4 w-4" />
                  <span>Login</span>
                </Link>
              )}
              
              {/* Mobile menu button */}
              <button 
                className="md:hidden text-theme-primary-text hover:text-theme-highlight transition duration-300"
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Side Navbar for Mobile */}
      <div className={`fixed inset-y-0 left-0 transform ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'} md:hidden z-50 w-64 bg-theme-background/95 backdrop-blur-xl transition-transform duration-300 ease-in-out border-r border-theme-accent`}>
        <div className="flex flex-col h-full">
          <div className="flex items-center justify-between p-4 border-b border-theme-accent">
            <div className="flex items-center">
              <div className="relative">
                <Heart className="h-6 w-6 text-theme-highlight" />
                <span className="absolute -top-1 -right-1">
                  <Sparkles className="h-3 w-3 text-yellow-400" />
                </span>
              </div>
              <span className="ml-2 text-lg font-bold text-white">SeraNova AI</span>
            </div>
            <button 
              className="text-theme-secondary-text hover:text-theme-primary-text" 
              onClick={() => setIsSidebarOpen(false)}
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="flex-1 overflow-y-auto py-4">
            <ul className="px-4 space-y-6">
              <li>
                <Link
                  to="/"
                  onClick={(e) => {
                    handleHomeClick(e);
                    setIsSidebarOpen(false);
                  }}
                  className="text-theme-secondary-text hover:text-theme-primary-text hover:bg-theme-accent/30 rounded-lg p-3 flex items-center transition duration-300"
                >
                  <HomeIcon className="h-5 w-5 mr-3" />
                  <span className="font-medium">Home</span>
                </Link>
              </li>
              <li>
                <Link
                  to="/chat"
                  className="text-theme-secondary-text hover:text-theme-primary-text hover:bg-theme-accent/30 rounded-lg p-3 flex items-center transition duration-300"
                  onClick={() => setIsSidebarOpen(false)}
                >
                  <MessageSquare className="h-5 w-5 mr-3" />
                  <span className="font-medium">Chat</span>
                </Link>
              </li>
              <li>
                <button
                  onClick={() => { setShowPlaylistModal(true); setIsSidebarOpen(false); }}
                  className="text-theme-secondary-text hover:text-theme-primary-text hover:bg-theme-accent/30 rounded-lg p-3 flex items-center transition duration-300 w-full text-left"
                >
                  <Music className="h-5 w-5 mr-3" />
                  <span className="font-medium">Playlist</span>
                </button>
              </li>
            </ul>
          </div>

          {/* Only show Login button on home page */}
          {isHomePage && (
            <div className="p-4 border-t border-theme-accent">
              <Link
                to="/login"
                className="w-full bg-theme-highlight hover:bg-theme-highlight/90 text-theme-background py-2 px-4 rounded-lg flex items-center justify-center space-x-2 transition duration-300"
                onClick={() => setIsSidebarOpen(false)}
              >
                <LogIn className="h-4 w-4" />
                <span>Login</span>
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Backdrop for mobile sidebar */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 md:hidden"
          onClick={() => setIsSidebarOpen(false)}
        ></div>
      )}

      {/* Playlist Modal */}
      <PlaylistModal 
        isOpen={showPlaylistModal} 
        onClose={() => setShowPlaylistModal(false)} 
      />
    </>
    
  );

};
export default Navbar;
