module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280', // neutral charcoal accent
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#0b1220'
        },
        accent: {
          DEFAULT: '#2f6fdb', // subtle cool blue accent
          600: '#265cc0'
        }
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif']
      }
    }
  },
  plugins: []
}
