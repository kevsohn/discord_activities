import pytest


@pytest.mark.asyncio
async def test_game_start(game_id, client, redis_client):
    import json

    # mock session manager
    session_id = "testsession123"
    user_info = {'user_id': "user1"}
    await redis_client.set(f"session:{session_id}", json.dumps(user_info))

    r = await client.get(f"/games/{game_id}/start",
                         headers={"Cookie": f"session_id={session_id}"})
    assert r.status_code == 200
    state = r.json()

    assert 'piece' in state
    assert 'rating' in state
    assert 'fen' in state
    assert state['ply'] == 0
    assert state['score'] == 0
    assert state['gameover'] == False


@pytest.mark.asyncio
async def test_game_update(game_id, client, redis_client):
    import json
    import chess

    session_id = "testsession456"
    user_info = {'user_id': "user2"}
    await redis_client.set(f"session:{session_id}", json.dumps(user_info))

    # start chess game to initialize state
    r = await client.get(f"/games/{game_id}/start",
                         headers={"Cookie": f"session_id={session_id}"})
    assert r.status_code == 200
    init_state = r.json()

    # make legal move
    move = 'e3e4'
    payload = {
        'state': init_state,
        'action': {'move': move}
    }

    # expected
    board = chess.Board(init_state['fen'])
    board.push_uci(move)

    r = await client.post(f"/games/{game_id}/update",
                          json=payload,
                          headers={"Cookie": f"session_id={session_id}"})
    assert r.status_code == 200
    state = r.json()

    if state.get('illegal'):
        print("Illegal move")

    assert state['fen'] == board.fen()
    assert state['ply'] == 1
    assert state['score'] == 0
    assert state['gameover'] == False


@pytest.mark.asyncio
async def test_house_turn(game_id, client, redis_client):
    import json
    import chess

    session_id = "testsession456"
    user_info = {'user_id': "user2"}
    await redis_client.set(f"session:{session_id}", json.dumps(user_info))

    # start chess game to initialize state
    r = await client.get(f"/games/{game_id}/start",
                         headers={"Cookie": f"session_id={session_id}"})
    assert r.status_code == 200
    init_state = r.json()

    # mock update call
    move = 'e3e4'
    board = chess.Board(init_state['fen'])
    board.push_uci(move)
    init_state['fen'] = board.fen()
    init_state['ply'] = 1

    # expected opp move
    house_move = 'f5e4'
    board.push_uci(house_move)

    payload = {'state': init_state}
    r = await client.post(f"/games/{game_id}/house_turn",
                          json=payload,
                          headers={"Cookie": f"session_id={session_id}"})
    assert r.status_code == 200
    state = r.json()

    assert state['house_move'] == house_move
    assert state['fen'] == board.fen()
    assert state['ply'] == 2
    assert state['score'] == 0
    assert state['gameover'] == False

