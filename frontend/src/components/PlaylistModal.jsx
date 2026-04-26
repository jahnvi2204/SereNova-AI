import React, { useState } from 'react';
import { Music, XCircle, ExternalLink, Loader } from 'lucide-react';
import { chatAPI } from '../api/api';

const PlaylistModal = ({ isOpen, onClose }) => {
  const [mood, setMood] = useState('');
  const [playlists, setPlaylists] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const moods = [
    { value: 'anxious', label: 'Anxious', color: 'bg-orange-500/20 text-orange-300' },
    { value: 'sad', label: 'Sad', color: 'bg-blue-500/20 text-blue-300' },
    { value: 'stressed', label: 'Stressed', color: 'bg-red-500/20 text-red-300' },
    { value: 'happy', label: 'Happy', color: 'bg-yellow-500/20 text-yellow-300' },
    { value: 'calm', label: 'Calm', color: 'bg-green-500/20 text-green-300' },
    { value: 'energetic', label: 'Energetic', color: 'bg-purple-500/20 text-purple-300' },
    { value: 'focused', label: 'Focused', color: 'bg-indigo-500/20 text-indigo-300' },
    { value: 'sleepy', label: 'Sleepy', color: 'bg-gray-500/20 text-gray-300' },
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
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="glass w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6 sm:p-8"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-white/[0.06] ring-1 ring-white/10">
              <Music className="text-zinc-200" size={22} />
            </span>
            <h2 className="text-lg font-semibold tracking-tight text-zinc-100">Playlists</h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-zinc-500 transition hover:text-zinc-200"
          >
            <XCircle size={24} />
          </button>
        </div>

        <p className="mb-6 text-sm text-zinc-500">
          Pick a mood to fetch playlist suggestions.
        </p>

        {/* Mood Selection */}
        <div className="mb-6">
          <h3 className="mb-3 text-xs font-semibold uppercase tracking-[0.2em] text-zinc-500">Mood</h3>
          <div className="mb-4 grid grid-cols-2 gap-2 md:grid-cols-4 md:gap-3">
            {moods.map((moodOption) => (
              <button
                key={moodOption.value}
                type="button"
                onClick={() => handleMoodSelect(moodOption.value)}
                disabled={isLoading}
                className={`rounded-2xl border p-3 text-left text-sm font-medium transition ${
                  mood === moodOption.value
                    ? `${moodOption.color} border-white/20 ring-1 ring-white/20`
                    : 'border-white/10 bg-white/[0.03] text-zinc-200 hover:border-white/20'
                } disabled:opacity-50`}
              >
                {moodOption.label}
              </button>
            ))}
          </div>

          <div className="flex gap-2">
            <input
              type="text"
              value={mood}
              onChange={(e) => setMood(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleCustomMood()}
              placeholder="Or type a mood…"
              className="flex-1 rounded-2xl border border-white/10 bg-black/30 px-4 py-2.5 text-sm text-zinc-100 placeholder:text-zinc-600 focus:border-white/20 focus:outline-none"
              disabled={isLoading}
            />
            <button
              type="button"
              onClick={handleCustomMood}
              disabled={isLoading || !mood.trim()}
              className="rounded-2xl bg-white px-4 py-2.5 text-sm font-medium text-zinc-950 transition hover:bg-zinc-100 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Go
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
            <Loader className="mb-4 animate-spin text-zinc-400" size={32} />
            <p className="text-sm text-zinc-500">Loading…</p>
          </div>
        )}

        {/* Playlists */}
        {!isLoading && playlists.length > 0 && (
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-zinc-200">Results</h3>
            {playlists.map((playlist, index) => (
              <div
                key={index}
                className="glass-tight p-4 transition hover:border-white/15"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0 flex-1">
                    <h4 className="mb-1 text-sm font-medium text-zinc-100">
                      {playlist.name}
                    </h4>
                    <p className="mb-2 text-sm text-zinc-500">
                      {playlist.description}
                    </p>
                    {playlist.mood && (
                      <span className="inline-block rounded-md border border-white/10 bg-white/[0.04] px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider text-zinc-400">
                        {playlist.mood}
                      </span>
                    )}
                  </div>
                  {playlist.spotify_url && (
                    <a
                      href={playlist.spotify_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex flex-shrink-0 items-center gap-2 rounded-xl border border-white/10 bg-emerald-500/15 px-3 py-2 text-xs font-medium text-emerald-200 transition hover:bg-emerald-500/25"
                    >
                      <ExternalLink size={16} />
                      Open
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {!isLoading && playlists.length === 0 && mood && (
          <div className="py-12 text-center">
            <Music className="mx-auto mb-4 text-zinc-600" size={40} />
            <p className="text-sm text-zinc-500">Choose a mood to load recommendations.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default PlaylistModal;

