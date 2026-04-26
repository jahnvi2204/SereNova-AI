import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, EyeOff, ChevronRight, Lock, Mail, ArrowRight } from 'lucide-react';
import { authAPI } from '../api/api';

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [formError, setFormError] = useState('');

  const [animateForm, setAnimateForm] = useState(false);
  const [lineIndex, setLineIndex] = useState(0);
  const lines = [
    'Clarity in every exchange.',
    'A quiet interface for real reflection.',
    'When you are ready, we are here.',
  ];

  useEffect(() => {
    setAnimateForm(true);
    const id = setInterval(() => {
      setLineIndex((i) => (i + 1) % lines.length);
    }, 5000);
    return () => clearInterval(id);
  }, [lines.length]);

  const handleSubmit = async () => {
    setFormError('');

    if (!email || !password) {
      setFormError('Please fill in all fields');
      return;
    }

    setIsLoading(true);

    try {
      await authAPI.login({ email, password });
      setIsLoading(false);
      navigate('/chat');
    } catch (error) {
      console.error('Login error:', error);
      setFormError(error.message || 'Sign in failed. Try again.');
      setIsLoading(false);
    }
  };

  return (
    <div className="app-mesh flex min-h-screen text-zinc-100">
      <div className="mesh-grid" />
      <div className="relative z-10 flex w-full flex-col justify-center p-6 md:w-1/2 md:p-12 lg:p-16">
        <div
          className={`mx-auto w-full max-w-md transition duration-700 ${
            animateForm ? 'translate-y-0 opacity-100' : 'translate-y-6 opacity-0'
          }`}
        >
          <div className="glass p-8 sm:p-10">
            <div className="mb-8 flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-400/25 to-indigo-500/25 ring-1 ring-white/10" />
              <div>
                <h1 className="text-lg font-semibold tracking-tight">SereNova</h1>
                <p className="text-xs text-zinc-500">Sign in</p>
              </div>
            </div>

            <h2 className="text-2xl font-semibold tracking-tight text-zinc-50">Welcome back</h2>
            <p className="mb-8 mt-1 text-sm text-zinc-500">Access your sessions.</p>

            {formError && (
              <div className="mb-4 rounded-2xl border border-red-500/30 bg-red-950/30 px-4 py-3 text-sm text-red-200">
                {formError}
              </div>
            )}

            <div className="space-y-5">
              <div className="space-y-2">
                <label htmlFor="email" className="block text-xs font-medium uppercase tracking-wider text-zinc-500">
                  Email
                </label>
                <div className="relative">
                  <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5">
                    <Mail className="h-4 w-4 text-zinc-500" />
                  </div>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="input-glass"
                    placeholder="you@company.com"
                    autoComplete="email"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label htmlFor="password" className="block text-xs font-medium uppercase tracking-wider text-zinc-500">
                    Password
                  </label>
                  <button
                    type="button"
                    className="text-xs text-zinc-500 transition hover:text-zinc-300"
                    onClick={() => {}}
                  >
                    Forgot?
                  </button>
                </div>
                <div className="relative">
                  <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5">
                    <Lock className="h-4 w-4 text-zinc-500" />
                  </div>
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="input-glass pr-11"
                    placeholder="••••••••"
                    autoComplete="current-password"
                  />
                  <div className="absolute inset-y-0 right-0 flex items-center pr-3">
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="text-zinc-500 transition hover:text-zinc-300"
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  className="h-4 w-4 rounded border-white/20 bg-white/5 text-emerald-500 focus:ring-emerald-500/30"
                />
                <label htmlFor="remember-me" className="text-sm text-zinc-500">
                  Keep me signed in
                </label>
              </div>

              <button
                type="button"
                onClick={handleSubmit}
                disabled={isLoading}
                className={`btn-primary w-full ${isLoading ? 'cursor-wait opacity-80' : ''}`}
              >
                {isLoading ? (
                  <>
                    <svg className="h-5 w-5 animate-spin text-zinc-900" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Signing in…
                  </>
                ) : (
                  <>
                    Sign in
                    <ChevronRight className="h-4 w-4" />
                  </>
                )}
              </button>

              <p className="pt-2 text-center text-sm text-zinc-500">
                New here?{' '}
                <button
                  type="button"
                  onClick={() => navigate('/signup')}
                  className="text-zinc-200 underline-offset-2 hover:underline"
                >
                  Create an account
                </button>
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="relative z-10 hidden w-1/2 flex-col justify-center p-12 md:flex">
        <div className="mx-auto w-full max-w-md">
          <div className="overflow-hidden rounded-[1.75rem] border border-white/[0.08] bg-white/[0.02] p-1">
            <div className="rounded-[1.5rem] bg-gradient-to-b from-zinc-900/80 to-black/40 p-8">
              <p className="text-xs font-semibold uppercase tracking-[0.25em] text-zinc-500">Session</p>
              <p className="mt-4 text-lg font-medium leading-relaxed text-zinc-200">
                {lines[lineIndex]}
              </p>
              <div className="mt-8 flex gap-1.5">
                {lines.map((_, i) => (
                  <span
                    key={i}
                    className={`h-0.5 flex-1 rounded-full ${i === lineIndex ? 'bg-white' : 'bg-zinc-700'}`}
                  />
                ))}
              </div>
            </div>
          </div>
          <p className="mt-8 text-sm leading-relaxed text-zinc-500">
            Design language: depth without noise, motion without gimmicks, contrast without harsh lines.
          </p>
          <a href="/" className="mt-6 inline-flex items-center gap-2 text-sm text-zinc-400 transition hover:text-zinc-200">
            <ArrowRight className="h-4 w-4 rotate-180" />
            Back to home
          </a>
        </div>
      </div>
    </div>
  );
};

export default Login;
