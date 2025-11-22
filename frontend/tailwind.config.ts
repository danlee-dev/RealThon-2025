import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#CCFF00',
          light: '#E0FF66',
          dark: '#99CC00',
        },
        secondary: {
          DEFAULT: '#FF00FF',
          light: '#FF66FF',
          dark: '#CC00CC',
        },
        accent: {
          DEFAULT: '#3B82F6',
          light: '#60A5FA',
          dark: '#2563EB',
        },
        background: {
          DEFAULT: '#FBFBFB',
          dark: '#111111',
        },
        ink: {
          DEFAULT: '#111111',
          light: '#333333',
        },
        primary: {
          DEFAULT: '#7C5CFC',
          light: '#9B7FFF',
          dark: '#5D3DD9',
        },
        sidebar: {
          DEFAULT: '#1A2440',
        },
        'light-grey': '#F5F6FA',
        orange: {
          DEFAULT: '#FF8D68',
        },
      },
    },
  },
  plugins: [],
}
export default config
