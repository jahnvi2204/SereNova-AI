import { useState, useEffect } from 'react';
import { Eye, EyeOff, Check, ChevronRight, ArrowRight, Lock, Mail, User } from 'lucide-react';
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
    "Personalized mental wellness support in a calm, focused space",
    "Create your account to continue your support journey",
    "Private conversations designed around your wellbeing",
    "Simple, structured guidance when you need support"
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
      <div className="app-mesh flex min-h-screen flex-col items-center justify-center p-6">
        <div className="mesh-grid" />
        <div className="glass relative z-10 w-full max-w-md p-8">
          <div className="flex flex-col items-center space-y-6 text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-500/15 ring-1 ring-white/10">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-emerald-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-zinc-100">You&apos;re in</h2>
            <p className="text-sm text-zinc-500">Welcome, {fullName}. Your account is ready.</p>
            <button
              type="button"
              className="btn-primary mt-2 w-full"
              onClick={() => { window.location.href = '/chat'; }}
            >
              <span>Continue to app</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    );
  }

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
              <p className="text-xs text-zinc-500">Create account</p>
            </div>
          </div>

          <h2 className="text-2xl font-semibold tracking-tight text-zinc-50">Sign up</h2>
          <p className="mb-8 mt-1 text-sm text-zinc-500">Minimal credentials. No clutter.</p>

          {formError && (
            <div className="mb-4 rounded-2xl border border-red-500/30 bg-red-950/30 px-4 py-3 text-sm text-red-200">
              {formError}
            </div>
          )}
          
          <div className="space-y-5">
            <div className="space-y-2">
              <label htmlFor="fullName" className="block text-xs font-medium uppercase tracking-wider text-zinc-500">Full name</label>
              <div className="relative">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5">
                  <User className="h-4 w-4 text-zinc-500" />
                </div>
                <input
                  id="fullName"
                  name="fullName"
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="input-glass"
                  placeholder="Your name"
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <label htmlFor="email" className="block text-xs font-medium uppercase tracking-wider text-zinc-500">Email</label>
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
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <label htmlFor="password" className="block text-xs font-medium uppercase tracking-wider text-zinc-500">Password</label>
              <div className="relative">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5">
                  <Lock className="h-4 w-4 text-zinc-500" />
                </div>
                <input
                  id="password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input-glass pr-11"
                  placeholder="Create a password"
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
              <label htmlFor="confirmPassword" className="block text-xs font-medium uppercase tracking-wider text-zinc-500">Confirm</label>
              <div className="relative">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5">
                  <Lock className="h-4 w-4 text-zinc-500" />
                </div>
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type={showConfirmPassword ? "text" : "password"}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="input-glass pr-11"
                  placeholder="Repeat password"
                />
                <div className="absolute inset-y-0 right-0 flex items-center pr-3">
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="text-zinc-500 transition hover:text-zinc-300"
                  >
                    {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
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
            
            <div className="flex items-start gap-3">
              <input
                id="terms"
                name="terms"
                type="checkbox"
                checked={acceptTerms}
                onChange={(e) => setAcceptTerms(e.target.checked)}
                className="mt-0.5 h-4 w-4 rounded border-white/20 bg-white/5 text-emerald-500 focus:ring-emerald-500/30"
              />
              <label htmlFor="terms" className="text-sm text-zinc-500">
                I accept the <span className="cursor-pointer text-zinc-300">Terms</span> and <span className="cursor-pointer text-zinc-300">Privacy</span>
              </label>
            </div>

            <button
              type="button"
              onClick={handleSubmit}
              disabled={isLoading}
              className={`btn-primary mt-2 w-full ${isLoading ? 'cursor-wait opacity-80' : ''}`}
            >
              {isLoading ? (
                <>
                  <svg className="mr-2 h-5 w-5 animate-spin text-zinc-900" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Creating account…
                </>
              ) : (
                <>
                  Create account
                  <ChevronRight className="h-4 w-4" />
                </>
              )}
            </button>

            <p className="mt-8 text-center text-sm text-zinc-500">
              Have an account?{' '}
              <a href="/login" className="text-zinc-200 underline-offset-2 hover:underline">Sign in</a>
            </p>
          </div>
          </div>
        </div>
      </div>

      <div className="relative z-10 hidden w-1/2 flex-col justify-center p-12 md:flex">
        <div className="mx-auto w-full max-w-lg">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-zinc-500">Product</p>
          <h3 className="mt-2 text-2xl font-semibold tracking-tight text-zinc-100">A composed experience</h3>
          <p className="mt-3 text-sm leading-relaxed text-zinc-500">
            Glass surfaces, tight typography, and restrained color keep attention on the conversation—not decoration.
          </p>
          <ul className="mt-8 space-y-4">
            {[
              'Structured session flow with calm hierarchy',
              'Private-by-design messaging surface',
              'Minimal UI chrome; fewer distractions',
            ].map((line) => (
              <li key={line} className="flex gap-3 text-sm text-zinc-400">
                <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-md bg-white/[0.06] ring-1 ring-white/10">
                  <Check className="h-3 w-3 text-emerald-400/90" />
                </span>
                {line}
              </li>
            ))}
          </ul>
          <div className="glass-tight mt-10 p-5">
            <p className="text-sm leading-relaxed text-zinc-500">
              <span className="text-zinc-300">Note.</span> {demoMessages[currentMessageIndex]}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Signup