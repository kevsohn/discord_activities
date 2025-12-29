export async function auth_user(discord_sdk) {
	// get auth code from discord client
	const { code } = await discord_sdk.commands.authorize({
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
	const auth = await discord_sdk.commands.authenticate({
		access_token
	});

	if (auth == null) {
		throw new Error("Authentication failed");
	}

	return auth;
}
