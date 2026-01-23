import { useEffect, useState } from "react";
import GameAPI from "../services/GameAPI";
import ErrorBoundary from "./ErrorBoundary";


export default function GameWrapper({ gameId, GameRenderer, gameConfig = {}, }) {
  const [model, setModel] = useState(null);
  const [resetRequired, setResetRequired] = useState(false);

  const { hasHouseTurn = false } = gameConfig;

  // --- Start game ---
  useEffect(() => {
    async function start() {
      try {
        const state = await GameAPI.start(gameId);
        setModel(state);
        setResetRequired(false);
      } catch (err) {
        console.error(err);
      }
    }
    start();
  }, [gameId]);


  // --- Send player action to backend ---
  async function dispatch(action) {
    if (!model || model.gameover || resetRequired) return;

    try {
      const next = await GameAPI.update(gameId, model, action);
      setModel(next);

      // Auto house turn
      if (
        hasHouseTurn &&
        !next.wrong &&
        !next.illegal &&
        !next.gameover
      ) {
        const house = await GameAPI.houseTurn(gameId, next);
        setModel(house);
      }
    } catch (err) {
      if (err.code === 409) {
        // epoch conflict / game reset
        setResetRequired(true);
      } else {
        console.error(err);
      }
    }
  }


  // --- Reset UI if epoch conflict ---
  if (resetRequired) {
    return (
      <div className="flex flex-col items-center gap-4 p-4 text-center">
        <div className="text-red-600 font-bold">
          Puzzle reset — click below to restart
        </div>
        <button
          className="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700"
          onClick={async () => {
            setResetRequired(false);
            const state = await GameAPI.start(gameId);
            setModel(state);
          }}
        >
          Restart Puzzle
        </button>
      </div>
    );
  }


  if (!model) return null;

  return (
    <ErrorBoundary>
      <GameRenderer model={model} dispatch={dispatch} />
    </ErrorBoundary>
  );
}

