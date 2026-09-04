/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          950: '#0a0d11',
          900: '#10151c',
          800: '#171e28',
          700: '#222b38',
        },
        copper: {
          300: '#e8c9a8',
          400: '#d4a574',
          500: '#c4894a',
          600: '#a86d34',
        },
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', 'Segoe UI', 'system-ui', 'sans-serif'],
        display: ['"IBM Plex Sans"', 'Segoe UI', 'sans-serif'],
      },
      boxShadow: {
        panel: '0 12px 40px rgba(0, 0, 0, 0.28)',
      },
    },
  },
  plugins: [],
}
