import { useMemo, useState, useEffect, useCallback } from "react";
import { Chess } from "chess.js";

const FILES = ["a","b","c","d","e","f","g","h"];

const PIECES = {
  p: "♟", r: "♜", n: "♞", b: "♝", q: "♛", k: "♚",
  P: "♙", R: "♖", N: "♘", B: "♗", Q: "♕", K: "♔",
};

/* ================== COLOR SYSTEM ================== */
const COLORS = {
  board: { light: "#f0d9b5", dark: "#b58863" },
  move: { primary: "#1f7a1f", captureOutline: "orange" },
  feedback: { correct: "#52c41a", wrong: "#ff4d4f" },
  piece: {
    white: "#ffffff",
    black: "#000000",
    whiteShadow: "0 0 2px #000, 0 0 4px #000",
    blackShadow: "0 0 2px #fff",
  },
};

/* ---------------- SQUARE ---------------- */
function Square({ piece, isLight, isSelected, isLegal, isCapture, flash, onClick }) {
  const baseColor = isLight ? COLORS.board.light : COLORS.board.dark;
  const pieceChar = piece ? (piece.color === "w" ? piece.type.toUpperCase() : piece.type) : null;

  return (
    <div
      onClick={onClick}
      style={{
        position: "relative",
        width: 60,
        height: 60,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: flash ? flash : isSelected ? COLORS.move.primary : baseColor,
        boxShadow: !flash && isCapture ? `inset 0 0 0 4px ${COLORS.move.captureOutline}` : "none",
        fontSize: 36,
        cursor: piece ? "pointer" : "default",
        color: piece ? (piece.color === "w" ? COLORS.piece.white : COLORS.piece.black) : undefined,
        textShadow: piece ? (piece.color === "w" ? COLORS.piece.whiteShadow : COLORS.piece.blackShadow) : undefined,
      }}
    >
      {!flash && isLegal && !isCapture && (
        <div style={{
          position: "absolute",
          width: 16,
          height: 16,
          borderRadius: "50%",
          backgroundColor: COLORS.move.primary,
        }} />
      )}
      {pieceChar && PIECES[pieceChar]}
    </div>
  );
}

/* ---------------- MAIN ---------------- */
export default function ChessPuzzleRenderer({ model, dispatch, features = {} }) {
  const DEFAULT_FEATURES = { showScore: true, showRating: true };
  const { showScore, showRating } = { ...DEFAULT_FEATURES, ...features };

  const chess = useMemo(() => new Chess(model.fen), [model.fen]);

  const [selectedSquare, setSelectedSquare] = useState(null);
  const [lastAttemptedTarget, setLastAttemptedTarget] = useState(null);
  const [flashSquares, setFlashSquares] = useState({});
  const [promotionMove, setPromotionMove] = useState(null);

  /* --- Disable highlighting if puzzle over --- */
  const moveMap = useMemo(() => {
    if (!selectedSquare || model.gameover) return [];
    return chess.moves({ square: selectedSquare, verbose: true });
  }, [selectedSquare, chess, model.gameover]);

  const legalMoves = moveMap.filter(m => !m.captured).map(m => m.to);
  const captureMoves = moveMap.filter(m => m.captured).map(m => m.to);

  const handleSquareClick = useCallback((square) => {
    if (model.gameover) return; // no interaction after finish

    const piece = chess.get(square);
    if (!selectedSquare) {
      if (piece) setSelectedSquare(square);
      return;
    }

    if (square === selectedSquare) {
      setSelectedSquare(null);
      return;
    }

    const move = moveMap.find(m => m.to === square);
    if (!move) return setSelectedSquare(null);

    if (move.flags.includes("p")) return setPromotionMove(move);

    setLastAttemptedTarget(square);
    dispatch({ move: move.from + move.to });
    setSelectedSquare(null);
  }, [selectedSquare, moveMap, chess, dispatch, model.gameover]);

  function choosePromotion(piece) {
    setLastAttemptedTarget(promotionMove.to);
    dispatch({ move: promotionMove.from + promotionMove.to + piece });
    setPromotionMove(null);
    setSelectedSquare(null);
  }

  useEffect(() => {
    if (!lastAttemptedTarget) return;
    const color = model.wrong ? COLORS.feedback.wrong : COLORS.feedback.correct;
    setFlashSquares({ [lastAttemptedTarget]: color });
    const t = setTimeout(() => setFlashSquares({}), 600);
    return () => clearTimeout(t);
  }, [model.wrong, lastAttemptedTarget]);

  const renderRanks = model.piece === "b" ? [...Array(8).keys()] : [...Array(8).keys()].reverse();
  const renderFiles = model.piece === "b" ? [...Array(8).keys()].reverse() : [...Array(8).keys()];

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
        <div></div>

        {/* FILE LABELS — styled like board UI */}
        {renderFiles.map(f => (
          <div key={f} style={{ display:"flex", alignItems:"center", justifyContent:"center", fontWeight:"bold" }}>
            {FILES[f].toUpperCase()}
          </div>
        ))}

        {renderRanks.map(r => (
          <div key={r} style={{ display: "contents" }}>
            <div style={{ display:"flex", alignItems:"center", justifyContent:"center", fontWeight:"bold" }}>
              {r + 1}
            </div>

            {renderFiles.map(f => {
              const square = FILES[f] + (r + 1);
              return (
                <Square
                  key={square}
                  piece={chess.get(square)}
                  isLight={(f + r) % 2 === 0}
                  isSelected={!model.gameover && selectedSquare === square}
                  isLegal={legalMoves.includes(square)}
                  isCapture={captureMoves.includes(square)}
                  flash={flashSquares[square]}
                  onClick={() => handleSquareClick(square)}
                />
              );
            })}
          </div>
        ))}
      </div>

      {/* INFO PANEL — centered */}
      <div className="text-sm space-y-1" style={{ display: "flex", justifyContent: "center", gap: 16 }}>
        {showRating && model.rating && <div>Rating: {model.rating}</div>}
        {showScore && <div>Mistakes: {model.score}</div>}
      </div>

      {model.gameover && (
        <div style={{ fontWeight: "bold", color: COLORS.feedback.correct }}>
          Puzzle Complete!
        </div>
      )}

      {promotionMove && (
        <div style={{ display: "flex", gap: 10 }}>
          {["q","r","b","n"].map(p => (
            <button key={p} onClick={() => choosePromotion(p)}>{p.toUpperCase()}</button>
          ))}
        </div>
      )}
    </div>
  );
}

