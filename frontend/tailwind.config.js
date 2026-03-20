/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary:  "#667eea",
        success:  "#43e97b",
        danger:   "#f44336",
        warning:  "#ff9800",
        dark:     { DEFAULT:"#0f0f1a", card:"#1a1a2e", card2:"#16213e", border:"#2a2a4a" },
        light:    { DEFAULT:"#f0faf4", card:"#ffffff", card2:"#f8fffe", border:"#e0e8f0" },
      },
      fontFamily: { poppins: ["Poppins", "sans-serif"] },
      animation: {
        "fade-in":    "fadeIn 0.2s ease",
        "slide-up":   "slideUp 0.2s ease",
        "count-up":   "countUp 1s ease",
        "pulse-slow": "pulse 2s infinite",
      },
      keyframes: {
        fadeIn:  { from:{ opacity:0 }, to:{ opacity:1 } },
        slideUp: { from:{ opacity:0, transform:"translateY(12px)" },
                   to:  { opacity:1, transform:"translateY(0)" } },
      }
    }
  },
  plugins: []
}
