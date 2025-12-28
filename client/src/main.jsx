import { DiscordSDK } from "@discord/embedded-app-sdk";

import "../style.css";


// Will eventually store the authenticated user's access_token
let auth;
const discordSdk = new DiscordSDK(import.meta.env.VITE_CLIENT_ID);


async function setupDiscordSdk() {
	await discordSdk.ready();
	console.log("Discord SDK is ready");

	// Authorize with Discord Client
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

	// Retrieve an access_token from your activity's server
	const r = await fetch("/api/auth/token", {
		method: "POST",
		headers: {"Content-Type": "application/json"},
		body: JSON.stringify({code}),
	});
	const { access_token } = await r.json();

	// Authenticate with Discord client (using the access_token)
	auth = await discordSdk.commands.authenticate({
		access_token,
	});

	if (auth == null) {
		throw new Error("Authenticate command failed");
	}

	try {
		const r = await fetch('/api/session/create', {
			method: 'POST',
			headers: {'Content-Type': 'application/json'},
			body: JSON.stringify({
				user_id: auth.user.id,
			})
		});

		if (!r.ok) {
			console.warn('Failed to create session: ', r.statusText);
		}
	}
	catch (err) {
		console.warn('Error in creating session: ', err);
	}
}

// loading screen
document.querySelector('#app').innerHTML = `
	<div>
	<h1>Loading...</h1>
	</div>
`;

// main
setupDiscordSdk()
	.then(() => {
		console.log("Discord SDK is authenticated");

		// can now make API calls within the scopes requested in setup
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
			<h1>OAuth Failed ❌</h1>
		  </div>
		`;
	});

	
discordSdk.events.on('disconnect', (reason) => {
	console.log('Disconnected: ', reason);	
	if (auth?.session_id) {
		fetch('/api/session/delete', {
			method: 'DELETE',
			credentials: 'include',  // session id in cookie
		})
		.catch(err => console.error('Error deleting session: ', err));
	}
});


