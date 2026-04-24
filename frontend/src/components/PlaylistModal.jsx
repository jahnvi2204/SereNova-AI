import React, { useState } from 'react';
import { Music, XCircle, ExternalLink, Loader } from 'lucide-react';
import { chatAPI } from '../api/api';

const PlaylistModal = ({ isOpen, onClose }) => {
  const [mood, setMood] = useState('');
  const [playlists, setPlaylists] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const moods = [
    { value: 'anxious', label: '😰 Anxious', color: 'bg-orange-500/20 text-orange-300' },
    { value: 'sad', label: '😢 Sad', color: 'bg-blue-500/20 text-blue-300' },
    { value: 'stressed', label: '😫 Stressed', color: 'bg-red-500/20 text-red-300' },
    { value: 'happy', label: '😊 Happy', color: 'bg-yellow-500/20 text-yellow-300' },
    { value: 'calm', label: '😌 Calm', color: 'bg-green-500/20 text-green-300' },
    { value: 'energetic', label: '⚡ Energetic', color: 'bg-purple-500/20 text-purple-300' },
    { value: 'focused', label: '🎯 Focused', color: 'bg-indigo-500/20 text-indigo-300' },
    { value: 'sleepy', label: '😴 Sleepy', color: 'bg-gray-500/20 text-gray-300' },
  ];

  const handleMoodSelect = async (selectedMood) => {
    setMood(selectedMood);
    setError('');
    setIsLoading(true);
    setPlaylists([]);

    try {
      const result = await chatAPI.getPlaylists(selectedMood);
      setPlaylists(result.playlists || []);
    } catch (err) {
      setError('Failed to load playlists. Please try again.');
      console.error('Playlist error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCustomMood = async () => {
    if (!mood.trim()) {
      setError('Please enter a mood');
      return;
    }
    await handleMoodSelect(mood.trim());
  };

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" 
      onClick={onClose}
    >
      <div 
        className="bg-theme-background rounded-xl shadow-2xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto" 
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Music className="text-theme-highlight" size={28} />
            <h2 className="text-2xl font-bold text-theme-primary-text">Mood-Based Playlists</h2>
          </div>
          <button
            onClick={onClose}
            className="text-theme-secondary-text hover:text-theme-primary-text transition"
          >
            <XCircle size={24} />
          </button>
        </div>

        <p className="text-theme-secondary-text mb-6">
          Select your current mood and we'll recommend Spotify playlists to help improve your mental wellbeing.
        </p>

        {/* Mood Selection */}
        <div className="mb-6">
          <h3 className="text-theme-primary-text font-semibold mb-3">Select Your Mood</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
            {moods.map((moodOption) => (
              <button
                key={moodOption.value}
                onClick={() => handleMoodSelect(moodOption.value)}
                disabled={isLoading}
                className={`p-3 rounded-lg border-2 transition-all ${
                  mood === moodOption.value
                    ? `${moodOption.color} border-theme-highlight`
                    : 'bg-theme-surface border-theme-accent hover:border-theme-highlight text-theme-primary-text'
                } disabled:opacity-50`}
              >
                <span className="text-sm font-medium">{moodOption.label}</span>
              </button>
            ))}
          </div>

          {/* Custom Mood Input */}
          <div className="flex gap-2">
            <input
              type="text"
              value={mood}
              onChange={(e) => setMood(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleCustomMood()}
              placeholder="Or type your mood..."
              className="flex-1 bg-theme-surface border border-theme-accent rounded-lg px-4 py-2 text-theme-primary-text placeholder:text-theme-secondary-text focus:outline-none focus:ring-2 focus:ring-theme-highlight"
              disabled={isLoading}
            />
            <button
              onClick={handleCustomMood}
              disabled={isLoading || !mood.trim()}
              className="px-4 py-2 bg-theme-highlight hover:bg-theme-highlight/90 text-theme-primary-text rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Search
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-4 p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-300 text-sm">
            {error}
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="flex flex-col items-center justify-center py-12">
            <Loader className="animate-spin text-theme-highlight mb-4" size={32} />
            <p className="text-theme-secondary-text">Finding the perfect playlists for you...</p>
          </div>
        )}

        {/* Playlists */}
        {!isLoading && playlists.length > 0 && (
          <div className="space-y-4">
            <h3 className="text-theme-primary-text font-semibold text-lg">
              Recommended Playlists
            </h3>
            {playlists.map((playlist, index) => (
              <div
                key={index}
                className="bg-theme-surface border border-theme-accent rounded-lg p-4 hover:border-theme-highlight transition"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <h4 className="text-theme-primary-text font-semibold text-lg mb-2">
                      {playlist.name}
                    </h4>
                    <p className="text-theme-secondary-text text-sm mb-3">
                      {playlist.description}
                    </p>
                    {playlist.mood && (
                      <span className="inline-block px-2 py-1 bg-theme-accent/30 rounded text-xs text-theme-primary-text">
                        Mood: {playlist.mood}
                      </span>
                    )}
                  </div>
                  {playlist.spotify_url && (
                    <a
                      href={playlist.spotify_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition flex-shrink-0"
                    >
                      <ExternalLink size={18} />
                      <span>Open</span>
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {!isLoading && playlists.length === 0 && mood && (
          <div className="text-center py-12">
            <Music className="mx-auto text-theme-secondary-text mb-4" size={48} />
            <p className="text-theme-secondary-text">
              Select a mood above to get personalized playlist recommendations
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default PlaylistModal;

