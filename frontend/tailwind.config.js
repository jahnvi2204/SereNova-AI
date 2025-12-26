/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        theme: {
          background: '#0B0F19',
          surface: '#121926',
          accent: '#353E57',
          'primary-text': '#E0E6F3',
          'secondary-text': '#A0A9BF',
          highlight: '#4C6EF5',
        },
      },
    },
  },
  plugins: [],
}

