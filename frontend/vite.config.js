import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [tailwindcss(), react()],
  server: {
    port: 5174,
    // Proxy API calls to the FastAPI backend to avoid CORS issues during dev
    proxy: {
      '/agent': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
