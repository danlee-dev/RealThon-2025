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
        // --- System Colors (From 'nalgae' - matches CSS Variables) ---
        border: "hsl(var(--border))",
        input: "hsl(var(--border))",
        ring: "hsl(var(--primary))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--error))",
          foreground: "hsl(var(--primary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--surface))",
          foreground: "hsl(var(--surface-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--surface))",
          foreground: "hsl(var(--surface-foreground))",
        },

        // --- Brand & Accent Colors (From 'dev') ---
        // Preserving 'dev' unique identities while avoiding conflict with system keywords
        brand: {
          DEFAULT: '#CCFF00', // Neon Lime (Matches --neon-lime in CSS)
          light: '#E0FF66',
          dark: '#99CC00',
        },
        // Renamed conflicting 'dev' primary/secondary to preserve access
        'brand-purple': { 
          DEFAULT: '#7C5CFC', // Previously 'primary' in dev
          light: '#9B7FFF',
          dark: '#5D3DD9',
        },
        'brand-blue': {
           DEFAULT: '#3B82F6', // Previously 'accent' in dev
           light: '#60A5FA',
           dark: '#2563EB',
        },
        
        // --- Utility Colors (From 'dev') ---
        sidebar: {
          DEFAULT: '#1A2440',
        },
        ink: {
          DEFAULT: '#111111',
          light: '#333333',
        },
        'light-grey': '#F5F6FA',
        orange: {
          DEFAULT: '#FF8D68',
        },

        // --- Aliases & Fallbacks ---
        surface: "hsl(var(--surface))",
        error: "hsl(var(--error))",
        success: "hsl(var(--success))",
        warning: "hsl(var(--warning))",
        // Mapping generic accent to brand-blue or secondary based on preference
        accent: {
          DEFAULT: "hsl(var(--secondary))", 
          foreground: "hsl(var(--secondary-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
}
export default config