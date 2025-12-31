import { useState } from "react";
import { Chess } from "chess.js";
import { Chessboard } from "react-chessboard";
import styles from "./style.module.css";

export default function ChessPuzzleUI({ game_id, api_client, state, set_state }) {
  const [house_turn, set_house_turn] = useState(false);
  const [house_animation, set_house_animation] = useState(null);
  const [feedback, set_feedback] = useState(null);
  
  const uci_to_move = (uci) => ({ from: uci.slice(0, 2), to: uci.slice(2, 4) });

  const is_players_piece = (piece) => {
    if (!piece) return false;
    return piece[0] === (state.start_colour?.[0] || "w");
  };

  async function on_piece_drop(from, to) {
    if (house_turn || state.gameover) return false;

    const uci = `${from}${to}`;
    const chess = new Chess(state.fen); // temporary chess instance for validation

    const move = chess.move({ from, to, promotion: "q" });
    if (!move) {
      set_feedback("illegal");
      return false;
    }

    set_feedback(null);

    // send move to backend
    const r = await api_client.update(game_id, { state, action: { move: uci } });

    if (r.illegal || r.wrong) {
      set_state(r); // backend fen overwrites
      set_feedback(r.illegal ? "illegal" : "wrong");
      return true;
    }

    set_state(r); // correct move
    set_house_turn(true);

    const house_r = await api_client.house_turn(game_id, { state: r });

    if (house_r.move) {
      set_house_animation(uci_to_move(house_r.move));
    }

    set_state(house_r);
    set_house_animation(null);
    set_house_turn(false);

    return true;
  }

  return (
    <div className={styles.container}>
      {house_turn && <div className={`${styles.overlay} ${styles.thinking}`}>House thinking…</div>}
      {feedback && (
        <div className={`${styles.overlay} ${styles[feedback]}`}>
          {feedback === "wrong" ? "Wrong move" : "Illegal move"}
        </div>
      )}

      <Chessboard
        position={state.fen}
        boardOrientation={state.start_colour}
        onPieceDrop={on_piece_drop}
        animationDuration={300}
        customAnimation={house_animation}
        arePiecesDraggable={!house_turn && !state.gameover}
        isDraggablePiece={({ piece }) => is_players_piece(piece)}
      />
    </div>
  );
}

