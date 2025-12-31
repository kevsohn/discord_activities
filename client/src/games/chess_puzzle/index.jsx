import GameInterface from "../game_interface";
import ChessPuzzleUI from "./UI";

export default function ChessPuzzle({ api_client }) {
    return (
        <GameInterface
            game_id="chess_puzzle"
            api_client={api_client}
            UI={ChessPuzzleUI}
        />
    );
}

