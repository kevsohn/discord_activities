import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
	plugins: [react()],

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
			'/games': {
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
