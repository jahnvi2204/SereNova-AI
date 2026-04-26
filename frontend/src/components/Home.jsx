import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { MessageSquare, Shield, ArrowRight, User, Send, Activity, Layers, Lock } from "lucide-react";
import Navbar from "./Navbar";
import { chatAPI, authAPI } from '../api/api';

const HomePage = () => {
  const navigate = useNavigate();
  const [loaded, setLoaded] = useState(false);
  const [previewMessage, setPreviewMessage] = useState('');
  const [previewChat, setPreviewChat] = useState([
    { text: "I'm here to listen. What's on your mind today?", isUser: false }
  ]);
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);

  useEffect(() => {
    if (authAPI.isAuthenticated()) {
      navigate('/chat');
    }
  }, [navigate]);

  useEffect(() => {
    setLoaded(true);
  }, []);

  const handlePreviewSubmit = async (e) => {
    if (e) e.preventDefault();
    if (!previewMessage.trim()) return;

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
        text: "Connection issue. Open the full app to continue.",
        isUser: false
      }]);
    } finally {
      setIsPreviewLoading(false);
    }
  };

  const partners = ['Vercel', 'Linear', 'Notion', 'Stripe', 'Raycast', 'Figma'];

  return (
    <div className="app-mesh">
      <div className="mesh-grid" />
      <Navbar />

      <main className="relative z-10 mx-auto w-full max-w-6xl px-4 pb-20 pt-28 md:pt-32">
        <div className="grid items-center gap-14 lg:grid-cols-2 lg:gap-10">
          <div className={`transition duration-1000 ${loaded ? 'translate-y-0 opacity-100' : 'translate-y-6 opacity-0'}`}>
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-1.5 text-xs font-medium text-zinc-300 backdrop-blur-md">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400/80" />
              Calm, structured support
            </div>

            <h1 className="text-4xl font-semibold leading-[1.1] tracking-tight text-zinc-50 sm:text-5xl lg:text-[3.25rem]">
              One place for
              <span className="block bg-gradient-to-r from-zinc-100 via-zinc-200 to-zinc-500 bg-clip-text text-transparent">
                thoughtful conversation
              </span>
            </h1>

            <p className="mt-6 max-w-lg text-base leading-relaxed text-zinc-400 sm:text-lg">
              A focused interface for reflection and support—no clutter, no noise. Private sessions, clear structure, and responses tuned for emotional clarity.
            </p>

            <div className="mt-10 flex flex-col gap-3 sm:flex-row sm:items-center">
              <a href="/chat" className="btn-primary shadow-glow">
                Open app
                <ArrowRight className="h-4 w-4" />
              </a>
              <a href="#interface" className="btn-ghost">
                How it works
              </a>
            </div>

            {/* Decorative node network – abstract, not data */}
            <div className="relative mt-16 hidden h-32 sm:block">
              <svg className="absolute left-0 top-0 h-full w-full text-white/20" viewBox="0 0 400 120" fill="none" aria-hidden>
                <path d="M40 60 L120 30 L200 70 L280 40 L360 60" stroke="currentColor" strokeWidth="0.5" />
                <circle cx="40" cy="60" r="3" className="fill-emerald-400/40" />
                <circle cx="120" cy="30" r="3" className="fill-white/30" />
                <circle cx="200" cy="70" r="3" className="fill-indigo-400/40" />
                <circle cx="280" cy="40" r="3" className="fill-white/25" />
                <circle cx="360" cy="60" r="3" className="fill-emerald-400/30" />
              </svg>
              <div className="absolute bottom-0 left-0 flex gap-6 text-[10px] font-medium uppercase tracking-widest text-zinc-600">
                <span>Clarity</span>
                <span>Continuity</span>
                <span>Privacy</span>
              </div>
            </div>
          </div>

          <div className={`relative transition delay-200 duration-1000 ${loaded ? 'translate-y-0 opacity-100' : 'translate-y-6 opacity-0'}`}>
            <div className="absolute -inset-4 rounded-[2rem] bg-gradient-to-br from-emerald-500/10 via-transparent to-indigo-500/10 blur-2xl" />
            <div className="glass relative overflow-hidden p-0">
              <div className="flex items-center justify-between border-b border-white/[0.06] px-5 py-4">
                <div className="flex items-center gap-2.5">
                  <span className="flex h-9 w-9 items-center justify-center rounded-2xl bg-white/[0.06] ring-1 ring-white/10">
                    <MessageSquare className="h-4 w-4 text-zinc-200" />
                  </span>
                  <div>
                    <p className="text-sm font-medium text-zinc-100">Session</p>
                    <p className="text-xs text-zinc-500">Preview</p>
                  </div>
                </div>
                <span className="rounded-full border border-white/10 bg-white/[0.04] px-2.5 py-0.5 text-[10px] font-medium uppercase tracking-wide text-zinc-400">
                  Live
                </span>
              </div>

              <div className="flex h-[22rem] flex-col bg-gradient-to-b from-white/[0.02] to-transparent p-4 sm:p-5">
                <div className="flex-1 space-y-3 overflow-y-auto pr-1">
                  {previewChat.map((message, index) => (
                    <div key={index} className={`flex items-end gap-2.5 ${message.isUser ? 'flex-row-reverse' : ''}`}>
                      {!message.isUser && (
                        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-white/[0.06] ring-1 ring-white/10">
                          <MessageSquare className="h-3.5 w-3.5 text-zinc-300" />
                        </div>
                      )}
                      <div
                        className={`max-w-[88%] rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed ${
                          message.isUser
                            ? 'bg-white text-zinc-900'
                            : 'border border-white/[0.06] bg-white/[0.04] text-zinc-200'
                        }`}
                      >
                        {message.text}
                      </div>
                      {message.isUser && (
                        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-zinc-700/80">
                          <User className="h-3.5 w-3.5 text-zinc-200" />
                        </div>
                      )}
                    </div>
                  ))}
                  {isPreviewLoading && (
                    <div className="flex items-end gap-2.5">
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-white/[0.06]">
                        <MessageSquare className="h-3.5 w-3.5 text-zinc-300" />
                      </div>
                      <div className="flex gap-1 rounded-2xl border border-white/[0.06] bg-white/[0.04] px-4 py-3">
                        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-zinc-400" />
                        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-zinc-400 [animation-delay:0.1s]" />
                        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-zinc-400 [animation-delay:0.2s]" />
                      </div>
                    </div>
                  )}
                </div>

                <form onSubmit={handlePreviewSubmit} className="mt-4">
                  <div className="relative">
                    <input
                      type="text"
                      value={previewMessage}
                      onChange={(e) => setPreviewMessage(e.target.value)}
                      placeholder="Write a message…"
                      disabled={isPreviewLoading}
                      className="w-full rounded-2xl border border-white/10 bg-black/20 py-3 pl-4 pr-12 text-sm text-zinc-100 placeholder:text-zinc-500 focus:border-white/20 focus:outline-none focus:ring-1 focus:ring-white/10"
                    />
                    <button
                      type="submit"
                      disabled={isPreviewLoading || !previewMessage.trim()}
                      className="absolute right-2 top-1/2 -translate-y-1/2 rounded-xl p-2 text-zinc-300 transition hover:bg-white/5 disabled:opacity-40"
                    >
                      <Send className="h-4 w-4" />
                    </button>
                  </div>
                  <p className="mt-2 text-center text-xs text-zinc-500">
                    <a href="/chat" className="text-zinc-300 underline-offset-2 hover:underline">Full experience</a>
                    {' · '}
                    Private by design
                  </p>
                </form>
              </div>
            </div>
          </div>
        </div>

        {/* Bento / insights – visual rhythm like reference, no fake metrics */}
        <section id="interface" className="mt-24 md:mt-32">
          <p className="text-center text-xs font-semibold uppercase tracking-[0.2em] text-zinc-500">Interface</p>
          <h2 className="mx-auto mt-3 max-w-2xl text-center text-2xl font-semibold text-zinc-100 sm:text-3xl">
            Built for focus
          </h2>
          <p className="mx-auto mt-3 max-w-xl text-center text-sm text-zinc-500">
            A calm layout, glass surfaces, and clear hierarchy—so the product feels intentional, not templated.
          </p>

          <div className="mt-12 grid gap-4 md:grid-cols-3 lg:grid-cols-4 lg:grid-rows-2">
            <div className="glass row-span-2 flex flex-col justify-between p-6 md:col-span-2 lg:col-span-2">
              <div>
                <div className="mb-4 inline-flex items-center gap-2 rounded-lg bg-white/[0.04] px-2 py-1 text-[10px] font-medium uppercase tracking-wider text-zinc-400">
                  <Activity className="h-3 w-3" />
                  State
                </div>
                <h3 className="text-lg font-medium text-zinc-100">Session continuity</h3>
                <p className="mt-2 text-sm text-zinc-500">Threads stay organized. Switch context without losing the narrative.</p>
              </div>
              <div className="mt-8 flex h-24 items-end gap-1.5">
                {[40, 65, 45, 80, 55, 90, 50].map((h, i) => (
                  <div
                    key={i}
                    className="flex-1 rounded-t-md bg-gradient-to-t from-emerald-500/20 to-emerald-400/40"
                    style={{ height: `${h}%` }}
                  />
                ))}
              </div>
            </div>

            <div className="glass flex flex-col p-6">
              <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-white/[0.05]">
                <Lock className="h-4 w-4 text-zinc-300" />
              </div>
              <h3 className="text-sm font-medium text-zinc-100">Confidentiality</h3>
              <p className="mt-1 text-xs text-zinc-500">Conversations are treated with care and minimal surface area.</p>
            </div>

            <div className="glass flex flex-col p-6">
              <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-white/[0.05]">
                <Layers className="h-4 w-4 text-zinc-300" />
              </div>
              <h3 className="text-sm font-medium text-zinc-100">Layered UI</h3>
              <p className="mt-1 text-xs text-zinc-500">Depth and blur to separate content from chrome.</p>
            </div>

            <div className="glass flex flex-col justify-between p-6 md:col-span-2 lg:col-span-2">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h3 className="text-sm font-medium text-zinc-100">Composed layout</h3>
                  <p className="mt-1 text-xs text-zinc-500">Grid, spacing, and type tuned for long-form reading.</p>
                </div>
                <Shield className="h-5 w-5 shrink-0 text-zinc-500" />
              </div>
              <div className="mt-6 flex gap-2">
                {['Read', 'Reflect', 'Respond'].map((t) => (
                  <span key={t} className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-1 text-[10px] font-medium text-zinc-400">
                    {t}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Wordmark row – stylistic, not claims */}
        <div className="mt-20 border-t border-white/[0.06] pt-12">
          <p className="text-center text-[10px] font-medium uppercase tracking-[0.25em] text-zinc-600">Stack & craft</p>
          <div className="mt-6 flex flex-wrap items-center justify-center gap-x-10 gap-y-4 opacity-40 grayscale">
            {partners.map((name) => (
              <span key={name} className="text-sm font-semibold tracking-tight text-zinc-400">
                {name}
              </span>
            ))}
          </div>
        </div>
      </main>

      <footer className="relative z-10 border-t border-white/[0.06] py-10">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-4 text-sm text-zinc-500 md:flex-row">
          <span className="text-zinc-400">SereNova</span>
          <span>© {new Date().getFullYear()}</span>
          <div className="flex gap-6">
            <span className="cursor-pointer transition hover:text-zinc-300">Privacy</span>
            <span className="cursor-pointer transition hover:text-zinc-300">Terms</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
