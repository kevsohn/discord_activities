import { DiscordSDK } from "@discord/embedded-app-sdk";
import { useEffect, useState } from "react";

import reg from '../../shared/game_reg.json'
import { authenticateUser } from "./services/Auth";
import SessionManager from "./services/SessionManager";
import LoadingScreen from "./components/LoadingScreen";

import GameWrapper from "./components/GameWrapper";
import ChessPuzzleRenderer from "./components/renderers/ChessPuzzle";
//import MinesweeperRenderer from "./components/renderers/Minesweeper";


const GAME_ID = reg.current_game;

const UIs = {
  chess_puzzle: ChessPuzzleRenderer,
  //minesweeper: MinesweeperRenderer,
};

const discordSdk = new DiscordSDK(import.meta.env.VITE_CLIENT_ID);


export default function App() {
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    async function setup() {
      try {
        await discordSdk.ready();
		console.log('Discord SDK is ready');

        const auth = await authenticateUser(discordSdk);
		console.log('User authenticated');
        
		const session = new SessionManager(auth);
        await session.start();
		console.log('Session started');

        setStatus("authenticated");
      }catch (err) {
        console.error(err);
        setStatus("error");
      }
    }

    setup();
  }, []);

  if (status === "loading") return <LoadingScreen />;
  if (status === "error") return <h1>Authentication Failed ❌</h1>;

  const config = reg.games[GAME_ID].config;
  const renderer = UIs[GAME_ID];

  return (
    <GameWrapper
      gameId={GAME_ID}
      GameRenderer={renderer}
      gameConfig={config}
    />
  );
}

