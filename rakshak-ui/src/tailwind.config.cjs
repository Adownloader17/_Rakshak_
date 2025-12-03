/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eef2ff', 100:'#e0e7ff', 500:'#2563eb'
        }
      },
      borderRadius: { xl: '1rem' }
    },
  },
  plugins: [],
}
