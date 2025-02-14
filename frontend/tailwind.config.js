/** @type {import('tailwindcss').Config} */
export default {
    content: [
      "./src/**/*.{html,js}",
    ],
    theme: {
      extend: {
        colors: {
          primary: "#7289DA", // Discord-like blue
          secondary: "#23272A", // Dark grey
          background: "#2C2F33", // Darker grey
          error: "#f04747",
          success: "#43B581",
        },
        borderRadius: {
          "xl": "12px",
        },
      },
    },
    plugins: [],
  };
  