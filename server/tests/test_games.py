import pytest


@pytest.mark.asyncio
async def test_game_start(game_id, client, redis_client):
    import json

    # mock session manager
    session_id = "testsession123"
    user_info = {'id': "user1"}
    await redis_client.set(f"session:{session_id}", json.dumps(user_info))

    r = await client.get(f"/games/{game_id}/start",
                         headers={"Cookie": f"session_id={session_id}"})
    assert r.status_code == 200
    state = r.json()

    assert 'fen' in state
    assert state['moves'] == []
    assert state['score'] == 0
    assert state['gameover'] == False
    assert state['won'] == False


@pytest.mark.asyncio
async def test_game_update(game_id, client, redis_client):
    import json
    from chess import Board

    session_id = "testsession456"
    user_info = {'id': "user2"}
    await redis_client.set(f"session:{session_id}", json.dumps(user_info))

    # start chess game to initialize state
    r = await client.get(f"/games/{game_id}/start",
                         headers={"Cookie": f"session_id={session_id}"})
    assert r.status_code == 200
    init_state = r.json()

    # make a probably illegal move in the puzzle
    move = 'e2e4'
    payload = {
        'state': init_state,
        'action': {"uci": move}
    }

    r = await client.post(f"/games/{game_id}/update",
                          json=payload,
                          headers={"Cookie": f"session_id={session_id}"})
    assert r.status_code == 200
    state = r.json()

    # expected
    board = Board(init_state['fen'])
    board.push_uci(move)
    expected_fen = board.fen()

    assert state['fen'] == expected_fen
    assert state['moves'] == [move]
    assert state['score'] == 0
    assert state['gameover'] == True
    assert state['won'] == False


