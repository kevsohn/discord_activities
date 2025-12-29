import { DiscordSDK } from "@discord/embedded-app-sdk";
import { useState, useEffect } from "react";

import { auth_user } from "./services/auth";
import { SessionController } from "./services/sessions";

import { GAME_ID } from './services/game_config';
import { ChessPuzzle } from './games/chess_puzzle';
//import { Minesweeper } from './games/minesweeper';


const GAMES = {
	chess_puzzle: ChessPuzzle,
	//minesweeper: Minesweeper,
};

const discord_sdk = new DiscordSDK(import.meta.env.VITE_CLIENT_ID);


export default function App() {
  const [status, set_status] = useState("loading");  // loading | authenticated | error
  const [user, set_user] = useState(null);

  // initial setup: Discord SDK, auth, session
  useEffect(() => {
    async function setup() {
      try {
        await discord_sdk.ready();
        console.log("Discord SDK ready");

        const auth = await auth_user(discord_sdk);
        set_user(auth.user);
		console.log('User authenticated');

        const session = new SessionController(auth);
        await session.start();
		console.log('Session started succesfully');
		
		set_status('authenticated');
      } 
	  catch (err) {
        console.error("Setup failed:", err);
        set_status("error");
      }
    }

    setup();
  }, []);


  // UI
  if (status === "loading") {
    return (
	  <div>
		<h2>Loading the best game ever...</h2>
		<div className="loading-bar-container">
		  <div className="loading-bar"></div>
		</div>
	  </div>
    );
  }

  if (status === "error") {
    return <h1>Authentication Failed ❌</h1>;
  }

  // authenticated
  return (
    <>
	  {Object.entries(GAMES).map(([game_id, UI]) => (
        <div
          key={game_id}
          style={{ display: GAME_ID === game_id ? "block" : "none" }}
        >
          <UI active={GAME_ID === game_id} user={user} />
        </div>
      ))}
    </>
  );

}
