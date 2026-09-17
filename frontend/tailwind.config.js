/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          950: '#1a1615',
          900: '#26211F',
          850: '#38302d',
          800: '#4a413d',
          700: '#5A524F',
          600: '#736965',
        },
        industrial: {
          amber: '#C87A5B',
          orange: '#B85D3B',
          gold: '#D48C70',
          dark: '#8C3D21',
          surface: '#FFFFFF',
          border: '#DCD5CD',
        },
        copper: {
          300: '#EDC7B7',
          400: '#DFA895',
          500: '#C87A5B',
          600: '#A85637',
        },
        story: {
          bg: '#F7F4EF',
          surface: '#EEE6DD',
          card: '#FFFFFF',
          cardWarm: '#FAF7F2',
          cardHover: '#F5EFE6',
          border: '#DCD5CD',
          accent: '#C87A5B',
          terracotta: '#C87A5B',
          terracottaSoft: '#EDC7B7',
          mineral: '#BAB2B5',
          slate: '#5A524F',
          ink: '#26211F',
          amber: '#C87A5B',
          bone: '#26211F',
          muted: '#8A817D',
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
        panel: '0 4px 20px -2px rgba(186, 178, 181, 0.25)',
        warm: '0 8px 30px -4px rgba(200, 122, 91, 0.15)',
        glow: '0 0 20px rgba(200, 122, 91, 0.18)',
      },
    },
  },
  plugins: [],
}

