import pytest


@pytest.mark.asyncio
async def test_streak_incr(game_id, redis_client):
    from src.services.reset import get_current_epoch
    from src.depends.streak import mark_played, incr_streak

    epoch = get_current_epoch()
    guard_key = f'game:{game_id}:played:{epoch}'
    lplayed_key = f'game:{game_id}:last_played_epoch'
    streak_key = f'game:{game_id}:streak'

    # ensure streak key is clean
    await redis_client.delete(streak_key)
    await redis_client.delete(guard_key)
    assert await redis_client.get(guard_key) == None

    # 1st play of the day
    await mark_played(game_id, redis_client)
    assert int(await redis_client.get(guard_key)) == 1
    assert (await redis_client.get(lplayed_key)).decode('utf-8') == epoch

    # other users play
    await mark_played(game_id, redis_client)
    await mark_played(game_id, redis_client)
    assert int(await redis_client.get(guard_key)) == 1
    assert (await redis_client.get(lplayed_key)).decode('utf-8') == epoch

    await incr_streak(game_id, epoch, redis_client)
    streak = int(await redis_client.get(streak_key))
    assert streak == 1
    assert int(await redis_client.get(guard_key)) == 1

    # should incr again since same epoch & no guard_key reset
    await incr_streak(game_id, epoch, redis_client)
    streak = int(await redis_client.get(streak_key))
    assert streak == 2


@pytest.mark.asyncio
async def test_streak_reset(game_id, redis_client):
    from src.services.reset import get_current_epoch
    from src.depends.streak import mark_played, incr_streak

    epoch = '2025-12-22'
    guard_key = f'game:{game_id}:played:{epoch}'
    lplayed_key = f'game:{game_id}:last_played_epoch'
    streak_key = f'game:{game_id}:streak'

    # mock mark_played for prev day
    await redis_client.set(guard_key, 1)
    await redis_client.set(lplayed_key, epoch)

    # mock save_stats_to_db()
    await incr_streak(game_id, epoch, redis_client)
    await redis_client.delete(guard_key)
    assert await redis_client.get(guard_key) == None
    streak = int(await redis_client.get(streak_key))
    assert streak == 1

    # next day
    epoch = '2025-12-23'
    guard_key = f'game:{game_id}:played:{epoch}'

    # mock save_stats_to_db()
    # should reset streak cuz no one's played next day
    await incr_streak(game_id, epoch, redis_client)
    await redis_client.delete(guard_key)
    streak = int(await redis_client.get(streak_key))
    assert streak == 0

    # today
    epoch = get_current_epoch()
    guard_key = f'game:{game_id}:played:{epoch}'

    # someone played
    await mark_played(game_id, redis_client)
    assert (await redis_client.get(lplayed_key)).decode('utf-8') == epoch

    # today reset
    await incr_streak(game_id, epoch, redis_client)
    streak = int(await redis_client.get(streak_key))
    assert streak == 1


@pytest.mark.asyncio
async def test_stats_endpoint(game_id, client, redis_client, db_session_factory):
    from src.services.reset import get_current_epoch
    from src.services.leaderboard import rank_player
    from src.services.save import save_stats_to_db

    # create mock live leaderboard
    epoch = get_current_epoch()
    user_scores = {"user1": 3, "user2": 5, "user3": 2}
    for uid, score in user_scores.items():
        await rank_player(game_id, uid, epoch, score, redis_client)

    # persist stats to db
    await save_stats_to_db(
        game_id=game_id,
        prev_epoch=epoch,
        outof=5,
        redis=redis_client,
        db_session_factory=db_session_factory,
    )

    # Should be sorted ascending for chess
    expected_order = [
            {'user_id': 'user3', 'score': 2},
            {'user_id': 'user1', 'score': 3},
            {'user_id': 'user2', 'score': 5}
    ]

    r = await client.get(f'/api/stats/{game_id}/daily')
    assert r.status_code == 200

    stats = r.json()  # date, rankings, max_score, streak
    assert stats['date'] == epoch
    assert stats['rankings'] == expected_order
    assert stats['outof'] == 5
    assert stats['streak'] == 0  # not 1 bc haven't mark_played, so no played key


