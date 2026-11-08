/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        ayur: {
          50: "#f3f7f4",
          100: "#e3eee5",
          200: "#c7dcce",
          300: "#9fc2ab",
          400: "#71a182",
          500: "#4f8462",
          600: "#3c694c",
          700: "#31543e",
          800: "#294333",
          900: "#23372b",
          950: "#101e16",
        },
        gold: {
          50: "#fdfbf4",
          100: "#faf4e4",
          200: "#f5e7c3",
          300: "#edd497",
          400: "#e2ba66",
          500: "#d49e3d",
          600: "#b97f30",
          700: "#925e27",
          800: "#774a25",
          900: "#633e22",
        }
      },
    },
  },
  plugins: [],
};

