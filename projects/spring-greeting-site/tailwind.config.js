/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './content/**/*.{js,ts,jsx,tsx,mdx}'
  ],
  theme: {
    extend: {
      colors: {
        blush: '#ffe7ef',
        petal: '#ffd8e8',
        lilac: '#efe3ff',
        sky: '#e7f4ff'
      },
      boxShadow: {
        soft: '0 12px 40px rgba(190, 158, 184, 0.18)'
      }
    },
  },
  plugins: [],
};
