/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
          950: '#082f49',
        },
        secondary: {
          50: '#fafaf9',
          100: '#f5f5f4',
          200: '#e7e5e4',
          300: '#d6d3d1',
          400: '#a8a29e',
          500: '#78716c',
          600: '#57534e',
          700: '#44403c',
          800: '#292524',
          900: '#1c1917',
          950: '#0c0a09',
        },
      },
      fontFamily: {
        sans: ['Inter', 'Noto Sans JP', 'system-ui', 'sans-serif'],
        serif: ['Merriweather', 'Noto Serif JP', 'serif'],
        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
      },
      typography: {
        DEFAULT: {
          css: {
            maxWidth: '100%',
            color: 'rgb(55 65 81)',
            '[class~="lead"]': {
              color: 'rgb(75 85 99)',
            },
            a: {
              color: 'rgb(14 165 233)',
              textDecoration: 'none',
              fontWeight: '500',
              '&:hover': {
                color: 'rgb(2 132 199)',
                textDecoration: 'underline',
              },
            },
            'h1, h2, h3, h4': {
              color: 'rgb(31 41 55)',
              fontWeight: '700',
            },
            h1: {
              fontSize: '2.25rem',
              marginBottom: '1rem',
            },
            h2: {
              fontSize: '1.875rem',
              marginBottom: '0.875rem',
            },
            h3: {
              fontSize: '1.5rem',
              marginBottom: '0.75rem',
            },
            code: {
              color: 'rgb(239 68 68)',
              backgroundColor: 'rgb(243 244 246)',
              paddingLeft: '0.25rem',
              paddingRight: '0.25rem',
              paddingTop: '0.125rem',
              paddingBottom: '0.125rem',
              borderRadius: '0.25rem',
              fontSize: '0.875em',
            },
            'code::before': {
              content: 'none',
            },
            'code::after': {
              content: 'none',
            },
            pre: {
              backgroundColor: 'rgb(31 41 55)',
              color: 'rgb(229 231 235)',
              overflow: 'auto',
              borderRadius: '0.5rem',
            },
            'pre code': {
              color: 'inherit',
              backgroundColor: 'transparent',
              padding: '0',
            },
            blockquote: {
              borderLeftColor: 'rgb(14 165 233)',
              borderLeftWidth: '0.25rem',
              fontStyle: 'italic',
              color: 'rgb(75 85 99)',
            },
          },
        },
        dark: {
          css: {
            color: 'rgb(209 213 219)',
            '[class~="lead"]': {
              color: 'rgb(156 163 175)',
            },
            a: {
              color: 'rgb(56 189 248)',
              '&:hover': {
                color: 'rgb(14 165 233)',
              },
            },
            'h1, h2, h3, h4': {
              color: 'rgb(243 244 246)',
            },
            code: {
              color: 'rgb(244 114 182)',
              backgroundColor: 'rgb(55 65 81)',
            },
            blockquote: {
              borderLeftColor: 'rgb(56 189 248)',
              color: 'rgb(156 163 175)',
            },
          },
        },
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-subtle': 'pulseSubtle 2s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        pulseSubtle: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.8' },
        },
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      screens: {
        'xs': '475px',
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
  darkMode: 'class',
}