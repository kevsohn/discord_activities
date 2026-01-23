'''
Read engines/base.py for info.
'''
from collections.abc import Callable, Awaitable
import redis.asyncio as Redis
import asyncio
import chess
import io
from math import ceil

from .base import GameEngine
from ..services.save import save_stats_to_db


class ChessPuzzleEngine(GameEngine):
    """
    Board must be given in FEN.
    Player moves and solutions must be in UCI.
    """
    def __init__(self,
                 game_id: str,
                 redis: Redis,
                 db_session,
                 fetcher: Callable[[], Awaitable[dict]]):
        super().__init__(game_id, redis, db_session)
        self._fetcher = fetcher   # = lambda: provider(http)
        self.start_fen: str | None = None
        self.solution: list[str] | None = None
        self.rating: int | None = None


    async def ensure_reset(self, cur_epoch: str) -> bool:
        '''
        Ensures the engine fetches new puzzle after reset time.
        Returns True if reset.
        '''
        # if in the same epoch, do nothing
        if self._epoch == cur_epoch:
            return False

        async with self._lock:
            # check again after lock just in case
            if self._epoch == cur_epoch:
                return False

            prev_epoch = self._epoch
            # on 1st run, no prev epoch so no persist
            if prev_epoch is not None:
                await save_stats_to_db(self._game_id,
                                       prev_epoch,
                                       self.get_max_turn(),
                                       self._redis,
                                       self._db_session_factory)
            # after b/c if persist fails, stats are not lost
            self._epoch = cur_epoch

            # fetch new puzzle and init
            puzzle = await self._fetcher()
            self.start_fen = puzzle['fen']
            self.solution = puzzle['solution']
            self.rating = puzzle['rating']
            return True


    def init_state(self) -> dict:
        start_colour = self.start_fen.split()[1]  # <FEN> <active_color> ...

        return {
            "fen": self.start_fen,
            "rating": self.rating,
            "ply": 0,    # no. half moves
            "score": 0,  # no. wrong tries (i.e. 0/max_turn == best)
            "gameover": False,
            "start_colour": 'white' if start_colour == 'w' else 'black',
        }


    def update_state(self, state: dict, action: dict) -> dict:
        if state['gameover']:
            return state

        board = chess.Board(state['fen'])

        # if illegal move, return given state
        move = chess.Move.from_uci(action['move'])  # chess.Move!!!
        if move not in board.legal_moves:
            return {**state, 'illegal': True}

        # if wrong move, score++ and return state to try again
        ply = state['ply']
        if ply >= len(self.solution) or move.uci() != self.solution[ply]:
            return {
                "fen": board.fen(),
                "rating": self.rating,
                "ply": ply,
                "score": state['score'] + 1,
                "gameover": False,
                "wrong": True,
            }

        # correct; set up opponent's turn
        board.push(move)
        ply += 1

        # check if last move
        gameover = ply >= len(self.solution)
        return {
            "fen": board.fen(),
            "rating": self.rating,
            "ply": ply,
            "score": state['score'],
            "gameover": gameover
        }


    def play_house_turn(self, state: dict):
        if state['gameover']:
            return state

        ply = state['ply']
        move = self.solution[ply]  # UCI!!!

        board = chess.Board(state['fen'])
        board.push_uci(move)

        return {
            'fen': board.fen(),
            "rating": self.rating,
            'ply': ply + 1,
            'score': state['score'],
            'gameover': state['gameover'],
            'house_move': move
        }


    def get_max_turn(self) -> int:
        if self.solution is None:
            raise RuntimeError('Engine not initialized')
        return ceil(len(self.solution)/2)

