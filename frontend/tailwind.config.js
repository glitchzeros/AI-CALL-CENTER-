/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'coffee-beige': '#F5F5DC',
        'coffee-khaki': '#F0E68C',
        'coffee-tan': '#D2B48C',
        'coffee-brown': '#8B4513',
        'coffee-sienna': '#A0522D',
        'coffee-green': '#8FBC8F',
        'coffee-blue': '#B0C4DE',
      },
      fontFamily: {
        'heading': ['Cinzel Decorative', 'serif'],
        'body': ['Vollkorn', 'serif'],
        'mono': ['Source Code Pro', 'monospace'],
      },
      boxShadow: {
        'paper': '0 4px 8px rgba(139, 69, 19, 0.1)',
        'ink': '0 2px 4px rgba(139, 69, 19, 0.2)',
      },
      backgroundImage: {
        'paper-texture': 'radial-gradient(circle at 20% 80%, rgba(210, 180, 140, 0.1) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(139, 69, 19, 0.05) 0%, transparent 50%)',
        'coffee-stain': 'radial-gradient(circle, rgba(210, 180, 140, 0.3) 0%, transparent 70%)',
      },
    },
  },
  plugins: [],
}