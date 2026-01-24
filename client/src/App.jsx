import { DiscordSDK } from "@discord/embedded-app-sdk";
import { useEffect, useState } from "react";

import reg from '../../shared/game_reg.json'
import { authenticateUser } from "./services/Auth";
import SessionManager from "./services/SessionManager";
import LoadingScreen from "./components/LoadingScreen";

import GameWrapper from "./components/GameWrapper";
import ChessPuzzleRenderer from "./components/renderers/ChessPuzzle";
//import MinesweeperRenderer from "./components/renderers/Minesweeper";


const discordSdk = new DiscordSDK(import.meta.env.VITE_CLIENT_ID);
const GAME_ID = reg.current_game;

const UIs = {
  chess_puzzle: ChessPuzzleRenderer,
  //minesweeper: MinesweeperRenderer,
};


export default function App() {
  const [status, setStatus] = useState("loading");
  const config = reg.games[GAME_ID].config;
  const renderer = UIs[GAME_ID];

  useEffect(() => {
    async function setup() {
      try {
        await discordSdk.ready();
		console.log('Discord SDK is ready');

        const auth = await authenticateUser(discordSdk);
		const session = new SessionManager(auth);
        await session.start();
		console.log('Session started');

        setStatus("authenticated");
      }catch (err) {
        console.error(err);
      }
    }

    setup();
  }, []);

  if (status === "loading") return <LoadingScreen />;

  return (
    <GameWrapper
      gameId={GAME_ID}
      GameRenderer={renderer}
      gameConfig={config}
    />
  );
}

