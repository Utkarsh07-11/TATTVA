/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          950: '#07090d',
          900: '#0c1017',
          850: '#111722',
          800: '#161f2e',
          700: '#222f44',
          600: '#33435c',
        },
        industrial: {
          amber: '#f59e0b',
          orange: '#ea580c',
          gold: '#d97706',
          dark: '#78350f',
          surface: '#0d1117',
          border: '#1f293d',
        },
        copper: {
          300: '#e8c9a8',
          400: '#d4a574',
          500: '#c4894a',
          600: '#a86d34',
        },
        story: {
          bg: '#07090d',
          card: '#0d1118',
          cardHover: '#131822',
          border: 'rgba(255, 255, 255, 0.08)',
          accent: '#d4a574',
          amber: '#f59e0b',
          bone: '#f1f3f6',
          muted: '#94a3b8',
        },
      },
      fontFamily: {
        sans: ['"Inter"', '"IBM Plex Sans"', 'system-ui', 'sans-serif'],
        condensed: ['"Inter"', '"IBM Plex Sans"', 'system-ui', 'sans-serif'],
        display: ['"Playfair Display"', 'Georgia', 'serif'],
        editorial: ['"Playfair Display"', 'Georgia', 'serif'],
        narrative: ['"Newsreader"', 'Georgia', 'serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'Menlo', 'monospace'],
      },
      boxShadow: {
        panel: '0 12px 40px rgba(0, 0, 0, 0.45)',
        glow: '0 0 20px rgba(245, 158, 11, 0.15)',
      },
    },
  },
  plugins: [],
}

