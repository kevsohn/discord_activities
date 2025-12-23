import pytest


@pytest.mark.asyncio
async def test_game_start(game_id, client, redis_client):
    # mock session manager
    session_id = "testsession123"
    user_id = "user1"
    await redis_client.set(f"session:{session_id}", user_id)

    r = await client.get(f"/games/{game_id}/start",
                                headers={"Cookie": f"session_id={session_id}"})

    assert r.status_code == 200
    data = r.json()
    assert "fen" in data
    assert "moves" in data
    assert data["score"] == 0
    assert data['gameover'] == False
    assert data['won'] == False


@pytest.mark.asyncio
async def test_game_update_advances_state(game_id, client, redis_client):
    session_id = "testsession456"
    user_id = "user2"

    await redis_client.set(f"session:{session_id}", user_id)

    # start game to initialize state
    await client.get(f"/games/{game_id}/start",
                     headers={"Cookie": f"session_id={session_id}"})

    payload = {
        "state": {"fen": 'start_fen', "moves": [], "score": 0, "gameover": False, "won": False},
        "action": {"uci": "e2e4"}
    }

    r = await client.post(f"/games/{game_id}/update",
                                 json=payload,
                                 headers={"Cookie": f"session_id={session_id}"})
    assert r.status_code == 200
    data = r.json()
    assert data["score"] == 1
    assert data["moves"] == ["e2e4"]


