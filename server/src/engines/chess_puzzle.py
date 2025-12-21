'''
Read engines/base.py for info.
'''
from collections.abc import Callable, Awaitable
import asyncio
from chess import Board

from .base import GameEngine
from ..services.save import save_stats


class ChessPuzzleEngine(GameEngine):
    """
    Board must be given in FEN.
    Player moves and solutions must be in UCI.
    """
    def __init__(self, game_id: str, fetcher: Callable[[], Awaitable[dict]]):
        super().__init__(game_id)
        self._fetcher = fetcher   # = lambda: provider(http)
        self.fen: str | None = None
        self.solution: list[str] | None = None


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
                await save_stats(self._game_id,
                                 prev_epoch,
                                 self.get_max_score())
            # after b/c if persist fails, stats are not lost
            self._epoch = cur_epoch

            # fetch new data and init
            data = await self._fetcher()
            self.fen = data['fen']
            self.solution = data['solution']
            return True


    def get_init_state(self) -> dict:
        return {
            "fen": self.fen,
            "moves": [],
            "score": 0,         # no. successful turns
            "gameover": False,
            "won": False
        }


    def update_state(self, state: dict, action: dict) -> dict:
        if state['gameover']:
            return state

        board = Board(state["fen"])
        move = action["uci"]
        i = len(state['moves'])  # i lags turn by 1

        # if wrong move, gameover
        if i >= len(self.solution) or move != self.solution[i]:
            return {**state, 'gameover': True, 'won': False}

        # correct
        board.push_uci(move)
        new_moves = state['moves'] + [move]
        new_score = i+1

        # check if last move
        if new_score == self.get_max_score():
            return {
                "fen": board.fen(),
                "moves": new_moves,
                "score": new_score,
                "gameover": True,
                "won": True
            }
        # cont
        return {
            "fen": board.fen(),
            "moves": new_moves,
            "score": new_score,
            "gameover": False,
            "won": False
        }


    def get_max_score(self) -> int:
        if self.solution is None:
            raise RuntimeError('Engine not initialized')
        return len(self.solution)

