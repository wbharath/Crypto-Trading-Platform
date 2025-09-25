/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#1f2937',
        secondary: '#374151',
        accent: '#10b981',
        danger: '#ef4444',
        success: '#22c55e'
      }
    }
  },
  plugins: []
}
