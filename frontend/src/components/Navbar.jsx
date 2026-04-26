import React, { useState, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { MessageSquare, Home, Music, LogIn, UserPlus, Menu, X } from "lucide-react";
import PlaylistModal from "./PlaylistModal";
import { authAPI } from '../api/api';

const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [isScrolled, setIsScrolled] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [showPlaylistModal, setShowPlaylistModal] = useState(false);

  const isHomePage = location.pathname === '/';

  const handleHomeClick = (e) => {
    if (authAPI.isAuthenticated()) {
      e.preventDefault();
      navigate('/chat');
    }
  };

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 24);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const navLink = "text-sm font-medium text-zinc-400 transition hover:text-white";

  return (
    <>
      <nav
        className={`fixed top-5 left-1/2 z-50 w-[min(92rem,94%)] -translate-x-1/2 transition-all duration-300 ${
          isScrolled ? "top-3" : "top-5"
        }`}
      >
        <div
          className={`flex items-center justify-between gap-4 rounded-full border border-white/[0.08] px-4 py-2.5 shadow-glow-sm backdrop-blur-2xl md:px-6 ${
            isScrolled ? "bg-black/55" : "bg-black/35"
          }`}
        >
          <Link to="/" onClick={handleHomeClick} className="flex items-center gap-2.5 shrink-0">
            <span className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-emerald-400/30 to-indigo-500/30 ring-1 ring-white/10" />
            <span className="text-sm font-semibold tracking-tight text-zinc-100">SereNova</span>
          </Link>

          <ul className="hidden items-center gap-8 md:flex">
            <li>
              <Link to="/" onClick={handleHomeClick} className={`${navLink} flex items-center gap-1.5`}>
                <Home className="h-3.5 w-3.5 opacity-60" />
                Home
              </Link>
            </li>
            <li>
              <Link to="/chat" className={`${navLink} flex items-center gap-1.5`}>
                <MessageSquare className="h-3.5 w-3.5 opacity-60" />
                Chat
              </Link>
            </li>
            <li>
              <button
                type="button"
                onClick={(e) => {
                  e.preventDefault();
                  setShowPlaylistModal(true);
                }}
                className={`${navLink} flex items-center gap-1.5`}
              >
                <Music className="h-3.5 w-3.5 opacity-60" />
                Playlists
              </button>
            </li>
          </ul>

          <div className="flex items-center gap-2 md:gap-3">
            {isHomePage && (
              <>
                <Link
                  to="/login"
                  className="hidden items-center gap-1.5 rounded-full px-3 py-1.5 text-sm font-medium text-zinc-300 transition hover:bg-white/5 hover:text-white sm:flex"
                >
                  <LogIn className="h-3.5 w-3.5" />
                  Sign in
                </Link>
                <Link
                  to="/signup"
                  className="inline-flex items-center gap-1.5 rounded-full bg-white px-4 py-2 text-sm font-medium text-zinc-950 transition hover:bg-zinc-100"
                >
                  <UserPlus className="h-3.5 w-3.5" />
                  Create account
                </Link>
              </>
            )}
            <button
              type="button"
              className="rounded-lg p-2 text-zinc-400 transition hover:bg-white/5 hover:text-white md:hidden"
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              aria-label="Menu"
            >
              {isSidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>
      </nav>

      <div
        className={`fixed inset-y-0 left-0 z-50 w-72 max-w-[85vw] border-r border-white/10 bg-[#050506]/95 backdrop-blur-2xl transition-transform duration-300 ease-out md:hidden ${
          isSidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex h-full flex-col p-5">
          <div className="mb-8 flex items-center justify-between">
            <span className="text-sm font-semibold text-zinc-100">SereNova</span>
            <button type="button" onClick={() => setIsSidebarOpen(false)} className="text-zinc-500" aria-label="Close">
              <X className="h-5 w-5" />
            </button>
          </div>
          <ul className="flex flex-1 flex-col gap-1">
            <li>
              <Link
                to="/"
                onClick={(e) => {
                  handleHomeClick(e);
                  setIsSidebarOpen(false);
                }}
                className="flex items-center gap-3 rounded-xl px-3 py-3 text-sm text-zinc-300 hover:bg-white/5"
              >
                <Home className="h-4 w-4" />
                Home
              </Link>
            </li>
            <li>
              <Link
                to="/chat"
                onClick={() => setIsSidebarOpen(false)}
                className="flex items-center gap-3 rounded-xl px-3 py-3 text-sm text-zinc-300 hover:bg-white/5"
              >
                <MessageSquare className="h-4 w-4" />
                Chat
              </Link>
            </li>
            <li>
              <button
                type="button"
                onClick={() => {
                  setShowPlaylistModal(true);
                  setIsSidebarOpen(false);
                }}
                className="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left text-sm text-zinc-300 hover:bg-white/5"
              >
                <Music className="h-4 w-4" />
                Playlists
              </button>
            </li>
          </ul>
          {isHomePage && (
            <div className="mt-auto space-y-2 border-t border-white/10 pt-4">
              <Link
                to="/login"
                onClick={() => setIsSidebarOpen(false)}
                className="flex w-full items-center justify-center gap-2 rounded-full border border-white/10 py-2.5 text-sm text-zinc-200"
              >
                <LogIn className="h-4 w-4" />
                Sign in
              </Link>
              <Link
                to="/signup"
                onClick={() => setIsSidebarOpen(false)}
                className="flex w-full items-center justify-center gap-2 rounded-full bg-white py-2.5 text-sm font-medium text-zinc-950"
              >
                Create account
              </Link>
            </div>
          )}
        </div>
      </div>

      {isSidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm md:hidden"
          onClick={() => setIsSidebarOpen(false)}
          role="presentation"
        />
      )}

      <PlaylistModal isOpen={showPlaylistModal} onClose={() => setShowPlaylistModal(false)} />
    </>
  );
};

export default Navbar;
