import { useMemo, useState, useEffect, useCallback } from "react";
import { Chess } from "chess.js";

const FILES = ["a","b","c","d","e","f","g","h"];

const PIECES = {
  p: "♟", r: "♜", n: "♞", b: "♝", q: "♛", k: "♚"
};

/* ================== COLORS ================== */
const COLORS = {
  board: { light: "#f0d9b5", dark: "#b58863" },
  move: {
    selected: "orange",
    primary: "#1f7a1f", // green for legal/capturable
    house: "#4da6ff",   // blue for opponent move
  },
  feedback: { correct: "#52c41a", wrong: "#ff4d4f" },
  piece: {
    white: "#f0f0f0", // softer white
    black: "#000000",
  },
};

/* ---------------- SQUARE ---------------- */
function Square({ square, piece, isLight, isSelected, isLegal, isCapture, isHouseMove, flash, onClick }) {
  const baseColor = isLight ? COLORS.board.light : COLORS.board.dark;

  const backgroundColor = flash
    ? flash
    : isSelected
      ? COLORS.move.selected
      : baseColor;

  let borderStyle = "none";
  if (isCapture) borderStyle = `3px solid ${COLORS.move.primary}`;
  else if (isHouseMove) borderStyle = `3px solid ${COLORS.move.house}`;

  const pieceColor = piece
    ? piece.color === "w"
      ? COLORS.piece.white
      : COLORS.piece.black
    : undefined;

  const pieceOutline = piece
    ? piece.color === "w"
      ? `
        0 0 2px rgba(0,0,0,0.8),
        0 0 4px rgba(0,0,0,0.6),
        0 0 6px rgba(0,0,0,0.5)
      `
      : "0 0 1px rgba(255,255,255,0.8), 0 0 2px rgba(255,255,255,0.5)"
    : "none";

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
        backgroundColor,
        border: borderStyle,
        fontSize: 36,
        cursor: piece ? "pointer" : "default",
        color: pieceColor,
        textShadow: pieceOutline,
        boxSizing: "border-box",
      }}
    >
      {!flash && isLegal && !isCapture && !isSelected && (
        <div
          style={{
            position: "absolute",
            width: 16,
            height: 16,
            borderRadius: "50%",
            backgroundColor: COLORS.move.primary,
          }}
        />
      )}
      {piece && PIECES[piece.type]}
    </div>
  );
}

/* ---------------- PROMOTION PANEL ---------------- */
function PromotionPanel({ move, choosePromotion }) {
  const cellSize = 60;
  const FILES = ["a","b","c","d","e","f","g","h"];
  const fileIdx = FILES.indexOf(move.from[0]);
  const x = 20 + fileIdx * cellSize;
  const top = 5;

  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top,
        display: "flex",
        gap: 5,
        padding: 5,
        backgroundColor: "#666",
        border: "2px solid #555",
        borderRadius: 6,
        zIndex: 10,
      }}
    >
      {["q","r","b","n"].map(p => (
        <div
          key={p}
          onClick={() => choosePromotion(p)}
          style={{
            width: 50,
            height: 50,
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            fontSize: 36,
            cursor: "pointer",
            userSelect: "none",
            color: COLORS.piece.white,
            textShadow: `
              0 0 2px rgba(0,0,0,0.9),
              0 0 4px rgba(0,0,0,0.7),
              0 0 6px rgba(0,0,0,0.5)
            `,
          }}
        >
          {PIECES[p]}
        </div>
      ))}
    </div>
  );
}

/* ---------------- MAIN COMPONENT ---------------- */
export default function ChessPuzzleRenderer({ model, dispatch, features = {} }) {
  const DEFAULT_FEATURES = { showScore: true, showRating: true };
  const { showScore, showRating } = { ...DEFAULT_FEATURES, ...features };

  const chess = useMemo(() => new Chess(model.fen), [model.fen]);

  const [selectedSquare, setSelectedSquare] = useState(null);
  const [lastAttemptedTarget, setLastAttemptedTarget] = useState(null);
  const [flashSquares, setFlashSquares] = useState({});
  const [promotionMove, setPromotionMove] = useState(null);
  const [houseMoveSquares, setHouseMoveSquares] = useState([]);

  /* ---------------- House move tracking ---------------- */
  useEffect(() => {
    if (model.house_move) {
      const from = model.house_move.slice(0, 2);
      const to = model.house_move.slice(2, 4);
      setHouseMoveSquares([from, to]);
    }
  }, [model.house_move]);

  /* ---------------- Move derivation ---------------- */
  const moveMap = useMemo(() => {
    if (!selectedSquare || model.gameover) return [];
    return chess.moves({ square: selectedSquare, verbose: true });
  }, [selectedSquare, chess, model.gameover]);

  const legalMoves = moveMap.filter(m => !m.captured).map(m => m.to);
  const captureMoves = moveMap.filter(m => m.captured).map(m => m.to);

  /* ---------------- Square click ---------------- */
  const handleSquareClick = useCallback((square) => {
    if (model.gameover) return;

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

    if (move.flags.includes("p")) {
      setPromotionMove(move);
      return;
    }

    setLastAttemptedTarget(square);
    dispatch({ move: move.from + move.to });
    setSelectedSquare(null);

    if (!model.wrong) setHouseMoveSquares([]);
  }, [selectedSquare, moveMap, chess, dispatch, model.wrong, model.gameover]);

  /* ---------------- Promotion ---------------- */
  function choosePromotion(piece) {
    setLastAttemptedTarget(promotionMove.to);
    dispatch({ move: promotionMove.from + promotionMove.to + piece });
    setPromotionMove(null);
    setSelectedSquare(null);
    setHouseMoveSquares([]);
  }

  /* ---------------- Flash feedback ---------------- */
  useEffect(() => {
    if (!lastAttemptedTarget) return;
    const color = model.wrong ? COLORS.feedback.wrong : COLORS.feedback.correct;
    setFlashSquares({ [lastAttemptedTarget]: color });
    const t = setTimeout(() => setFlashSquares({}), 600);
    return () => clearTimeout(t);
  }, [model.wrong, lastAttemptedTarget]);

  /* ---------------- Board rendering ---------------- */
  const renderRanks = model.piece === "b" ? [...Array(8).keys()] : [...Array(8).keys()].reverse();
  const renderFiles = model.piece === "b" ? [...Array(8).keys()].reverse() : [...Array(8).keys()];
  const cellSize = 60;

  return (
    <div style={{
      position: "relative",
      minHeight: "100vh",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "flex-start", // top-aligned for compact layout
      paddingTop: 20,
    }}>
      {/* Chess Board */}
      <div style={{
        display: "grid",
        gridTemplateColumns: `20px repeat(8, ${cellSize}px)`,
        gridTemplateRows: `20px repeat(8, ${cellSize}px)`,
        width: 500,
        height: 500,
        border: "2px solid black",
        userSelect: "none",
        marginBottom: 4,
      }}>
        <div></div>
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
              const piece = chess.get(square);
              const isLegal = legalMoves.includes(square);
              const isCapture = captureMoves.includes(square);
              const isHouseMove = houseMoveSquares.includes(square);

              return (
                <Square
                  key={square}
                  square={square}
                  piece={piece}
                  isLight={(f + r) % 2 === 0}
                  isSelected={!model.gameover && selectedSquare === square}
                  isLegal={isLegal}
                  isCapture={isCapture}
                  isHouseMove={isHouseMove}
                  flash={flashSquares[square]}
                  onClick={() => handleSquareClick(square)}
                />
              );
            })}
          </div>
        ))}
      </div>

      {/* Info Panel */}
      <div style={{
        display: "flex",
        justifyContent: "center",
        gap: 10,
        fontSize: 16,
        marginBottom: 0,
      }}>
        {showRating && model.rating && <div>Rating: {model.rating}</div>}
        {showScore && <div>Mistakes: {model.score}</div>}
      </div>

      {/* Puzzle Complete */}
      {model.gameover && (
        <div style={{
          fontWeight: "bold",
          color: COLORS.feedback.correct,
          fontSize: 18,
          marginTop: 0,
        }}>
          Puzzle Complete!
        </div>
      )}

      {/* Promotion Panel */}
      {promotionMove && <PromotionPanel move={promotionMove} choosePromotion={choosePromotion} />}
    </div>
  );
}

