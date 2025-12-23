import pytest


@pytest.mark.asyncio
async def test_streak_increments_once_per_day(game_id, redis_client):
    from server.src.depends.streak import mark_played, incr_streak

    epoch = "2025-12-22@00"

    # ensure streak key is clean
    await redis_client.delete(f"game:{game_id}:streak")
    await redis_client.delete(f"game:{game_id}:played:{epoch}")

    # first user plays
    await mark_played(game_id, redis_client)
    await incr_streak(game_id, epoch, redis_client)
    streak = int(await redis_client.get(f"game:{game_id}:streak"))
    assert streak == 1

    # second user plays same epoch, streak should not increment
    await mark_played(game_id, redis_client)
    await incr_streak(game_id, epoch, redis_client)
    streak = int(await redis_client.get(f"game:{game_id}:streak"))
    assert streak == 1


@pytest.mark.asyncio
async def test_leaderboard_zadd(redis_client):
    from server.src.services.leaderboard import rank_player
    from server.src.services.reset import get_current_epoch

    game_id = "chess_puzzle"
    epoch = get_current_epoch()
    user_scores = {"user1": 3, "user2": 5, "user3": 2}

    for uid, score in user_scores.items():
        await rank_player(game_id, uid, epoch, score, redis_client)

    key = f"game:{game_id}:leaderboard:{epoch}"
    rankings = await redis_client.zrevrange(key, 0, -1, withscores=True)
    # Should be sorted descending
    expected_order = [("user2", 5.0), ("user1", 3.0), ("user3", 2.0)]
    assert rankings == expected_order


@pytest.mark.asyncio
async def test_stats_endpoint(client, redis_client, db_session):
    from server.src.services.reset import get_current_epoch

    game_id = "chess_puzzle"
    epoch = get_current_epoch()

    await redis_client.zadd(
        f"game:{game_id}:leaderboard:{epoch}",
        {"user1": 2}
    )

    await save_stats(
        game_id=game_id,
        prev_epoch=epoch,
        max_score=5,
        redis=redis_client,
        db_session=db_session,
    )

    res = await client.get(f"/api/stats/{game_id}/daily")
    assert res.status_code == 200

    data = res.json()
    assert data["max_score"] == 5
    assert data["rankings"][0]["user"] == "user1"


