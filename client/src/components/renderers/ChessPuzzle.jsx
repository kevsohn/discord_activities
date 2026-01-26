import { useMemo, useState, useEffect } from "react";
import { Chess } from "chess.js";

const PIECES = {
  p: "♟", r: "♜", n: "♞", b: "♝", q: "♛", k: "♚",
  P: "♙", R: "♖", N: "♘", B: "♗", Q: "♕", K: "♔",
};

const FILES = ["a","b","c","d","e","f","g","h"];
const RANKS = [1,2,3,4,5,6,7,8];

export default function ChessPuzzleRenderer({ model, dispatch, features = {} }) {
  const DEFAULT_FEATURES = {
    showScore: true,
    showRating: true,
    highlightLegalMoves: true,
  };
  const { showScore, showRating, highlightLegalMoves } = { ...DEFAULT_FEATURES, ...features };

  const isBlackStart = model.piece === "b";
  const chess = useMemo(() => new Chess(model.fen), [model.fen]);

  const [selectedSquare, setSelectedSquare] = useState(null);
  const [lastAttemptedTarget, setLastAttemptedTarget] = useState(null);
  const [flashSquares, setFlashSquares] = useState({}); // { square: "red" | "green" }

  /* ---------------- LEGAL MOVES ---------------- */
  const legalTargets = useMemo(() => {
    if (!highlightLegalMoves || !selectedSquare) return [];
    return chess.moves({ square: selectedSquare, verbose: true }).map(m => m.to);
  }, [selectedSquare, chess, highlightLegalMoves]);

  /* ---------------- CLICK HANDLING ---------------- */
  function onSquareClick(fileIdx, rankIdx) {
    const square = FILES[fileIdx] + (rankIdx + 1);
    const piece = chess.get(square);

    if (!selectedSquare) {
      if (piece) setSelectedSquare(square);
      return;
    }

    if (square === selectedSquare) {
      setSelectedSquare(null);
      return;
    }

    setLastAttemptedTarget(square);
    dispatch({ move: selectedSquare + square });
    setSelectedSquare(null);
  }

  /* ---------------- FLASH LOGIC ---------------- */
  useEffect(() => {
    if (!lastAttemptedTarget) return;
    const color = model.wrong ? "#ff4d4f" : "#52c41a"; // red or green flash
    setFlashSquares({ [lastAttemptedTarget]: color });
    const t = setTimeout(() => setFlashSquares({}), 600);
    return () => clearTimeout(t);
  }, [model.wrong, lastAttemptedTarget]);

  /* ---------------- RENDER ORDER ---------------- */
  const renderRanks = isBlackStart ? [...Array(8).keys()] : [...Array(8).keys()].reverse();
  const renderFiles = isBlackStart ? [...Array(8).keys()].reverse() : [...Array(8).keys()];

  const cellSize = 60;

  return (
    <div className="flex flex-col items-center gap-3" style={{ minHeight: "100vh", justifyContent: "center" }}>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "20px repeat(8, 60px)",
          gridTemplateRows: "20px repeat(8, 60px)",
          width: 500,
          height: 500,
          border: "2px solid black",
          userSelect: "none",
        }}
      >
        {/* Top-left corner */}
        <div></div>

        {/* File labels */}
        {renderFiles.map(fIdx => (
          <div key={fIdx} style={{ display:"flex", alignItems:"center", justifyContent:"center", fontWeight:"bold" }}>
            {FILES[fIdx].toUpperCase()}
          </div>
        ))}

        {/* Board squares */}
        {renderRanks.map(rIdx => (
          <div key={rIdx} style={{ display: "contents" }}>
            <div style={{ display:"flex", alignItems:"center", justifyContent:"center", fontWeight:"bold" }}>
              {rIdx + 1}
            </div>

            {renderFiles.map(fIdx => {
              const square = FILES[fIdx] + (rIdx + 1);
              const piece = chess.get(square);

              const isSelected = selectedSquare === square;
              const isLegal = legalTargets.includes(square);
              const isLight = (fIdx + rIdx) % 2 === 0;
              const flash = flashSquares[square];

              let pieceChar = null;
              if (piece) pieceChar = piece.color === "w" ? piece.type.toUpperCase() : piece.type;

              return (
                <div
                  key={square}
                  onClick={() => onSquareClick(fIdx, rIdx)}
                  style={{
                    width: cellSize,
                    height: cellSize,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    backgroundColor: flash
                      ? flash
                      : isSelected
                        ? "orange"
                        : isLegal
                          ? "rgba(0,255,0,0.25)"
                          : isLight ? "#f0d9b5" : "#b58863", // Lichess colors
                    fontSize: 36,
                    cursor: piece ? "pointer" : "default",
                    color: piece
                      ? piece.color === "w"
                        ? "#fff"
                        : "#000"
                      : undefined,
                    textShadow: piece
                      ? piece.color === "w"
                        ? "0 0 2px #000, 0 0 4px #000"
                        : "0 0 2px #fff"
                      : undefined,
                    transition: "background-color 0.3s",
                  }}
                >
                  {pieceChar && PIECES[pieceChar]}
                </div>
              );
            })}
          </div>
        ))}
      </div>

      {/* Info panel centered */}
      <div className="text-sm space-y-1" style={{ display: "flex", justifyContent: "center", gap: 16 }}>
        {showRating && model.rating && <div>Rating: {model.rating}</div>}
        {showScore && <div>Mistakes: {model.score}</div>}
      </div>

      {model.gameover && <div className="font-bold text-green-600">Puzzle Complete!</div>}
    </div>
  );
}

