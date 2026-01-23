import { useMemo, useState } from "react";
import { Chess } from "chess.js";

// Unicode pieces
const PIECES = {
  p: "♟", r: "♜", n: "♞", b: "♝", q: "♛", k: "♚",
  P: "♙", R: "♖", N: "♘", B: "♗", Q: "♕", K: "♔",
};

// Convert FEN to 8x8 array
function fenToGrid(fen) {
  const board = [];
  fen.split(" ")[0].split("/").forEach(row => {
    const squares = [];
    for (const c of row) {
      if (/\d/.test(c)) {
        for (let i = 0; i < parseInt(c, 10); i++) squares.push(null);
      } else squares.push(c);
    }
    board.push(squares);
  });
  return board;
}

export default function ChessPuzzleRenderer({ model, dispatch, features = {} }) {
  const DEFAULT_FEATURES = {
    showScore: true,
    showRating: true,
    animateHouseMoves: true,
    highlightLegalMoves: true,
  };
  const { showScore, showRating, highlightLegalMoves } = { ...DEFAULT_FEATURES, ...features };

  const [selectedSquare, setSelectedSquare] = useState(null);

  const chess = useMemo(() => new Chess(model.fen), [model.fen]);
  const grid = useMemo(() => fenToGrid(model.fen), [model.fen]);

  // Flip board based on start color
  const displayRows = useMemo(() => {
    return model.start_colour?.toLowerCase() === "black" ? [...grid].reverse() : grid;
  }, [grid, model.start_colour]);

  const displayGrid = useMemo(() => {
    return model.start_colour?.toLowerCase() === "black"
      ? displayRows.map(row => [...row].reverse())
      : displayRows;
  }, [displayRows, model.start_colour]);

  // Column and row labels
  const files = ["a","b","c","d","e","f","g","h"];
  const ranks = [1,2,3,4,5,6,7,8];

  const displayFiles = model.start_colour?.toLowerCase() === "black" ? [...files].reverse() : files;
  const displayRanks = model.start_colour?.toLowerCase() === "black" ? ranks : [...ranks].reverse();

  // Legal moves from selected square
  const legalTargets = useMemo(() => {
    if (!highlightLegalMoves || !selectedSquare) return [];
    return chess.moves({ square: selectedSquare, verbose: true }).map(m => m.to);
  }, [selectedSquare, chess, highlightLegalMoves]);

  // Click handler
  function onSquareClick(file, rank) {
    const square = String.fromCharCode(97 + file) + (8 - rank);
    if (!selectedSquare) {
      if (chess.get(square)) setSelectedSquare(square);
      return;
    }

    const uci = selectedSquare + square;
    setSelectedSquare(null);
    dispatch({ move: uci });
  }

  return (
    <div className="flex flex-col items-center gap-3" style={{ minHeight: "100vh", justifyContent: "center" }}>
      {/* Board with labels */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "20px repeat(8, 60px)",
          gridTemplateRows: "20px repeat(8, 60px)",
          width: 500,
          height: 500,
          pointerEvents: "auto",
          userSelect: "none",
          border: "2px solid black",
          transform: "translateZ(0)",
        }}
      >
        {/* Top-left empty corner */}
        <div></div>

        {/* Top file labels */}
        {displayFiles.map(f => (
          <div key={f} style={{ display: "flex", alignItems: "center", justifyContent: "center", fontWeight: "bold" }}>
            {f.toUpperCase()}
          </div>
        ))}

        {/* Rows */}
        {displayRanks.map((rank, rIdx) => (
          <>
            {/* Left rank label */}
            <div key={`rank-${rank}`} style={{ display: "flex", alignItems: "center", justifyContent: "center", fontWeight: "bold" }}>
              {rank}
            </div>

            {/* Squares */}
            {displayGrid[rIdx].map((piece, file) => {
              const square = String.fromCharCode(97 + file) + (8 - rIdx);
              const isSelected = selectedSquare === square;
              const isLegal = legalTargets.includes(square);
              const isLight = (rIdx + file) % 2 === 0;
              const pieceColor = piece ? (piece === piece.toUpperCase() ? "#fff" : "#000") : undefined;

              return (
                <div
                  key={square}
                  onClick={() => onSquareClick(file, rIdx)}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    backgroundColor: isSelected
                      ? "orange"
                      : isLegal
                        ? "rgba(0,255,0,0.4)"
                        : isLight
                          ? "#f0d9b5"
                          : "#b58863",
                    fontSize: 36,
                    cursor: piece ? "pointer" : "default",
                    color: pieceColor,
                    textShadow: piece ? "0 0 3px rgba(0,0,0,0.7)" : undefined,
                    transition: "background-color 0.2s",
                  }}
                >
                  {piece && PIECES[piece]}
                </div>
              );
            })}
          </>
        ))}
      </div>

      {/* Score / rating */}
      <div className="text-sm space-y-1">
        {showScore && <div>Tries: {model.score}</div>}
        {showRating && model.rating && <div>Rating: {model.rating}</div>}
      </div>

      {/* Game over */}
      {model.gameover && <div className="font-bold text-green-600">Puzzle Complete!</div>}
    </div>
  );
}

