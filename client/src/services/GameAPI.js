const BASE = "/games";

async function request(url, options = {}) {
  // include credentials in cookie, otherwise no session id
  const res = await fetch(url, {
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  // handle case when reset time passes during game
  if (!res.ok) {
    const text = await res.text();
    if (res.status === 409) {
      const err = new Error("Game reset, restart required");
      err.code = 409;
      throw err;
    }
    throw new Error(text || res.statusText);
  }

  return res.json();
}


const GameAPI = {
  start(gameId) {
    return request(`${BASE}/${gameId}/start`);
  },

  update(gameId, state, action) {
    return request(`${BASE}/${gameId}/update`, {
      method: "POST",
      body: JSON.stringify({ state, action }),
    });
  },

  // optional
  houseTurn(gameId, state) {
    return request(`${BASE}/${gameId}/house_turn`, {
      method: "POST",
      body: JSON.stringify({ state }),
    });
  },
};


export default GameAPI;

