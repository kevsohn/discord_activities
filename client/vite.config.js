import {defineConfig} from 'vite';

// https://vitejs.dev/config/
export default defineConfig({
  server: {
	host: true,
	allowedHosts: [
		'.trycloudflare.com',
	],

    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        ws: true,
      },
    },

    hmr: {
	  protocol: 'wss',
      clientPort: 443,
    },
  },
});
