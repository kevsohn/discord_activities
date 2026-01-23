import { useMemo, useState, useEffect } from "react";
import { Chess } from "chess.js";

const PIECES = {
  p: "♟", r: "♜", n: "♞", b: "♝", q: "♛", k: "♚",
  P: "♙", R: "♖", N: "♘", B: "♗", Q: "♕", K: "♔",
};

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
    highlightLegalMoves: true,
  };
  const { showScore, showRating, highlightLegalMoves } = { ...DEFAULT_FEATURES, ...features };

  const [selectedSquare, setSelectedSquare] = useState(null);
  const [grid, setGrid] = useState(fenToGrid(model.fen));
  const [flashSquares, setFlashSquares] = useState({}); // { e4: "red" | "green" }

  const [lastAttemptedTarget, setLastAttemptedTarget] = useState(null);
  const [lastMoveTarget, setLastMoveTarget] = useState(null);

  const chess = useMemo(() => new Chess(model.fen), [model.fen]);

  useEffect(() => {
    setGrid(fenToGrid(model.fen));
  }, [model.fen]);

  const isBlackStart = model.start_colour?.toLowerCase() === "black";
  const displayRows = useMemo(() => (isBlackStart ? [...grid].reverse() : grid), [grid, isBlackStart]);
  const displayGrid = useMemo(() => (isBlackStart ? displayRows.map(r => [...r].reverse()) : displayRows), [displayRows, isBlackStart]);

  const files = ["a","b","c","d","e","f","g","h"];
  const ranks = [1,2,3,4,5,6,7,8];
  const displayFiles = isBlackStart ? [...files].reverse() : files;
  const displayRanks = isBlackStart ? ranks : [...ranks].reverse();

  const legalTargets = useMemo(() => {
    if (!highlightLegalMoves || !selectedSquare) return [];
    return chess.moves({ square: selectedSquare, verbose: true }).map(m => m.to);
  }, [selectedSquare, chess, highlightLegalMoves]);

  // Handle user clicks
  function onSquareClick(file, rank) {
    const square = String.fromCharCode(97 + file) + (8 - rank);
    const pieceHere = displayGrid[rank][file];

    if (!selectedSquare) {
      if (pieceHere !== null) setSelectedSquare(square);
      return;
    }

    if (selectedSquare === square) {
      setSelectedSquare(null);
      return;
    }

    // Track last attempted target for wrong flash
    setLastAttemptedTarget(square);

    const uci = selectedSquare + square;
    dispatch({ move: uci });

    setSelectedSquare(null);
  }

  // Flash logic
  useEffect(() => {
    let flashSquare = null;
    let color = null;

    if (model.wrong && lastAttemptedTarget) {
      flashSquare = lastAttemptedTarget;
      color = "red";
    } else if (!model.wrong && lastAttemptedTarget) {
      flashSquare = lastAttemptedTarget;
      color = "green";
    }

    if (flashSquare) {
      setFlashSquares({ [flashSquare]: color });
      const timer = setTimeout(() => setFlashSquares({}), 600);
      return () => clearTimeout(timer);
    }
  }, [model.wrong, lastAttemptedTarget]);

  const cellSize = 60;

  return (
    <div className="flex flex-col items-center gap-3" style={{ minHeight: "100vh", justifyContent: "center", position: "relative" }}>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "20px repeat(8, 60px)",
          gridTemplateRows: "20px repeat(8, 60px)",
          width: 500,
          height: 500,
          border: "2px solid black",
          userSelect: "none",
          position: "relative",
        }}
      >
        <div></div>
        {displayFiles.map(f => (
          <div key={f} style={{ display: "flex", alignItems: "center", justifyContent: "center", fontWeight: "bold" }}>
            {f.toUpperCase()}
          </div>
        ))}

        {displayRanks.map((rank, rIdx) => (
          <div key={rank} style={{ display: "contents" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", fontWeight: "bold" }}>
              {rank}
            </div>
            {displayGrid[rIdx].map((piece, file) => {
              const square = String.fromCharCode(97 + file) + (8 - rIdx);
              const isSelected = selectedSquare === square;
              const isLegal = legalTargets.includes(square);
              const isLight = (rIdx + file) % 2 === 0;
              const flashColor = flashSquares[square];

              return (
                <div
                  key={square}
                  onClick={() => onSquareClick(file, rIdx)}
                  style={{
                    width: cellSize,
                    height: cellSize,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    backgroundColor: isSelected
                      ? "orange"
                      : isLegal
                        ? "rgba(0,255,0,0.2)"
                        : isLight
                          ? "#f0d9b5"
                          : "#b58863",
                    fontSize: 36,
                    cursor: piece ? "pointer" : "default",
                    color: piece ? (piece === piece.toUpperCase() ? "#fff" : "#000") : undefined,
                    textShadow: piece ? "0 0 3px rgba(0,0,0,0.7)" : undefined,
                    transition: "background-color 0.3s",
                    position: "relative",
                  }}
                >
                  {piece && PIECES[piece]}

                  {/* Flash overlay */}
                  {flashColor && (
                    <div style={{
                      position: "absolute",
                      top: 0,
                      left: 0,
                      width: "100%",
                      height: "100%",
                      backgroundColor: flashColor,
                      opacity: 0.5,
                      pointerEvents: "none",
                      zIndex: 1,
                    }} />
                  )}
                </div>
              );
            })}
          </div>
        ))}
      </div>

      <div className="text-sm space-y-1">
        {showScore && <div>Tries: {model.score}</div>}
        {showRating && model.rating && <div>Rating: {model.rating}</div>}
      </div>

      {model.gameover && <div className="font-bold text-green-600">Puzzle Complete!</div>}
    </div>
  );
}

