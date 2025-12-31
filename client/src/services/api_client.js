export const api_client = {
    start: (game_id) =>
        fetch(`/games/${game_id}/start`, { method: "GET" }).then((r) => r.json()),

    update: (game_id, payload) =>
        fetch(`/games/${game_id}/update`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        }).then((r) => r.json()),

    house_turn: (game_id, payload) =>
        fetch(`/games/${game_id}/house_turn`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        }).then((r) => r.json()),

	gameover: (game_id) =>
        fetch(`/games/${game_id}/gameover`, { method: "GET" }).then((r) => r.json()),
};

