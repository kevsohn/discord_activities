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
  const response = await fetch("/api/auth/token", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      code,
    }),
  });
  const { access_token } = await response.json();

  // Authenticate with Discord client (using the access_token)
  auth = await discordSdk.commands.authenticate({
    access_token,
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
setupDiscordSdk()
  .then(() => {
    console.log("Discord SDK is authenticated");
	// We can now make API calls within the scopes we requested in setupDiscordSDK()

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

	


