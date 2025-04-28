import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import history from 'connect-history-api-fallback'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  
  server: {
    watch: {
      usePolling: true,
    },
    proxy: {
      '/diagnose': 'http://localhost:8000'
    },
    middlewareMode: false, // デフォルトなので省略可だけど一応明示
    setupMiddlewares(middlewares) {
      middlewares.unshift(
        history({
          disableDotRule: true,
          htmlAcceptHeaders: ['text/html', 'application/xhtml+xml'],
        })
      );
      return middlewares;
    }
  }
})
