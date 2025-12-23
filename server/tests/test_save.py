import pytest


@pytest.mark.asyncio
async def test_save_stats(game_id, redis_client, db_session):
    from server.src.services.save import save_stats
    from server.src.db.models.stats import Stats

    epoch = "2025-12-22@00"
    max_score = 10

    await redis_client.set(f"game:{game_id}:streak", 5)
    await redis_client.set(f"game:{game_id}:leaderboard:{epoch}", '[{"user":"user1","score":3}]')

    await save_stats(game_id, epoch, max_score, redis_client, db_session)

    # Check DB entry
    async with db_session.begin():
        res = await db_session.execute(
            select(Stats).where(Stats.game_id == game_id)
        )
        row = res.scalar_one()
        assert row.streak == 5
        assert row.max_score == 10

