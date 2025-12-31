export default function GameOverScreen({ result }) {
    return (
        <div>
            <h2>🎉 Game Over</h2>
            <p>{result === "won" ? "You won!" : result}</p>
        </div>
    );
}

