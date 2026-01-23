import { useEffect, useMemo, useState } from "react";
import { Chess } from "chess.js";
import { Chessboard } from "react-chessboard";


const DEFAULT_FEATURES = {
  showScore: true,
  showRating: true,
  animateHouseMoves: true,
  highlightLegalMoves: true,
};


export default function ChessPuzzleRenderer({ model, dispatch, features = {}, }) {
  const {
    showScore,
    showRating,
    animateHouseMoves,
    highlightLegalMoves,
  } = { ...DEFAULT_FEATURES, ...features };

  const [boardFen, setBoardFen] = useState(model.fen);
  const [selectedSquare, setSelectedSquare] = useState(null);


  // sync backend → board (animate house moves)
  // react-chessboard handles animation
  useEffect(() => {
    if (!animateHouseMoves) {
      setBoardFen(model.fen);
      return;
    }

    const delay = model.move ? 250 : 0;
    const id = setTimeout(() => setBoardFen(model.fen), delay);
    return () => clearTimeout(id);
  }, [model.fen, model.move, animateHouseMoves]);


  // highlight legal moves
  const chess = useMemo(() => new Chess(boardFen), [boardFen]);
  const legalSquares = useMemo(() => {
    if (!highlightLegalMoves || !selectedSquare) return {};
    const moves = chess.moves({ square: selectedSquare, verbose: true });

    return Object.fromEntries(
      moves.map(m => [
        m.to,
        { backgroundColor: "rgba(0, 255, 0, 0.3)" },
      ])
    );
  }, [selectedSquare, chess, highlightLegalMoves]);


  // either selects square if none selected
  // or sends move if square targetted 
  function onSquareClick(square) {
    if (!selectedSquare) {
      if (chess.get(square)) setSelectedSquare(square);
      return;
    }

    const uci = selectedSquare + square;
    setSelectedSquare(null);
    dispatch({ move: uci });
  }


  // revert player move on wrong/illegal
  useEffect(() => {
    if (model.wrong || model.illegal) {
      setBoardFen(model.fen);
    }
  }, [model.wrong, model.illegal]);


  return (
    <div className="flex flex-col items-center gap-3">
      <Chessboard
        position={boardFen}
        boardOrientation={model.start_colour}
        onSquareClick={onSquareClick}
        customSquareStyles={legalSquares}
        animationDuration={animateHouseMoves ? 300 : 0}
      />

      <div className="text-sm space-y-1">
        {showScore && <div>Score: {model.score}</div>}
        {showRating && model.rating && (
          <div>Rating: {model.rating}</div>
        )}
      </div>

      {model.gameover && (
        <div className="font-bold text-green-600">
          Puzzle Complete!
        </div>
      )}
    </div>
  );
}

