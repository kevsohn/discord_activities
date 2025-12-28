import { DiscordSDK } from "@discord/embedded-app-sdk";
import { createRoot } from 'react-dom/client';
import App from './App';

import '../style.css'
import { auth_user } from './services/auth';
import { SessionController } from './services/sessions';


const discordSdk = new DiscordSDK(import.meta.env.VITE_CLIENT_ID);
let auth;

const root = createRoot(document.getElementById('app'));


// render loading screen
root.render(<App status='loading'/>);


// setup SDK & session
async function setup() {
	try {
		await discordSdk.ready();
		console.log("Discord SDK is ready");

		auth = await auth_user(discordSdk);
		console.log("User authenticated");

		const session = new SessionController({ discordSdk, auth });
		session.start();
		console.log('Session created');

		root.render(<App status='authenticated' user={auth.user}/>);
	}catch (err) {
		console.error(err);
		root.render(<App status='error'/>);
	}
}


// main
setup();

