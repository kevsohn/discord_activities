export default function App({ status, user }) {
    if (status === "loading") {
        return (
            <div id="app">
				<h2>Loading the best game ever…</h2>
                <div className="loading-bar-container">
					<div className='loading-bar'></div>
				</div>
            </div>
        );
    }

    if (status === "error") {
        return (
            <div id="app">
                <h1>Authentication Failed ❌</h1>
            </div>
        );
    }

    // Authenticated
    return (
        <div id="app">
            <h1>Authenticated ✅</h1>
            <p>Welcome, {user.username}</p>
        </div>
    );
}

