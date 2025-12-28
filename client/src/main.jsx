import { DiscordSDK } from "@discord/embedded-app-sdk";
import { SessionController } from './services/sessions';

import "../style.css";


const discordSdk = new DiscordSDK(import.meta.env.VITE_CLIENT_ID);
let auth;
let session;


// setup SDK & session
async function setup() {
	await discordSdk.ready();
	console.log("Discord SDK is ready");

	await authenticate();
	console.log("User authenticated");

	session = new SessionController({
		discordSdk, 
		auth
	});
	session.start()
		.catch(err => {
			console.error('Failed to start session:', err);
		});
	console.log('Session created')
}


async function authenticate() {
	// get auth code from discord client
	const { code } = await discordSdk.commands.authorize({
		client_id: import.meta.env.VITE_CLIENT_ID,
		response_type: "code",
		state: "",
		prompt: "none",
		scope: [
		  "identify",
		  "guilds",
		  "applications.commands"
		],
	});

	// exchange code for access_token from backend
	const r = await fetch("/api/auth/token", {
		method: "POST",
		headers: {"Content-Type": "application/json"},
		body: JSON.stringify({code}),
	});
	const { access_token } = await r.json();

	// authenticate with access token
	auth = await discordSdk.commands.authenticate({
		access_token
	});
	if (auth == null) {
		throw new Error("Authenticate command failed");
	}
}


// loading screen
document.querySelector('#app').innerHTML = `
	<div>
	<h1>Loading...</h1>
	</div>
`;


// main
setup()
	.then(() => {
		console.log('Setup complete')

		document.querySelector('#app').innerHTML = `
			<div>
				<h1>Authenticated ✅</h1>
		  	</div>
		`;
	})
	.catch(err => {
		console.error("OAuth failed:", err);

		document.querySelector('#app').innerHTML = `
			<div>
				<h1>Auth Failed ❌</h1>
		  	</div>
		`;
	});

