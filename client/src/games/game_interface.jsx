import { useEffect, useState } from "react";
import GameOverScreen from "./gameover_screen";


export default function GameInterface({ game_id, api_client, UI }) {
    const [game_state, set_game_state] = useState(null);

    useEffect(() => {
        let is_active = true;

        async function load_game() {
            try {
                const state = await api_client.start(game_id);
                if (is_active) set_game_state(state);
            }catch (err) {
                console.error("Failed to start game:", err);
            }
        }

        load_game();

        return () => {
            is_active = false; // prevent state updates after unmount
        };
    }, [game_id, api_client]);

    if (!game_state) return null;

    if (game_state.gameover) {
        return <GameOverScreen result={game_state.result} />;
    }

    return (
        <UI
            game_id={game_id}
            api_client={api_client}
            state={game_state}
            set_state={set_game_state}
        />
    );
}

