/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        '4xl': '2rem',
      },
      boxShadow: {
        glow: '0 0 80px -20px rgba(16, 185, 129, 0.15)',
        'glow-sm': '0 0 40px -10px rgba(99, 102, 241, 0.12)',
      },
      backgroundImage: {
        'grid-faint': 'linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)',
        'radial-bloom': 'radial-gradient(ellipse 80% 50% at 50% -20%, rgba(16, 185, 129, 0.12), transparent 50%)',
        'radial-bloom-2': 'radial-gradient(ellipse 60% 40% at 100% 0%, rgba(99, 102, 241, 0.1), transparent 45%)',
      },
      colors: {
        theme: {
          background: '#040406',
          surface: 'rgba(12, 12, 16, 0.72)',
          'surface-solid': '#0c0c10',
          accent: 'rgba(255, 255, 255, 0.08)',
          'primary-text': '#F4F4F5',
          'secondary-text': '#A1A1AA',
          highlight: '#E4E4E7',
        },
        brand: {
          mint: '#34d399',
          indigo: '#6366f1',
        },
      },
    },
  },
  plugins: [],
}

