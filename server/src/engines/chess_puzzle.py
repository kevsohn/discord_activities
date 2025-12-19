'''
Read engines/base.py for info.
'''
from asyncio import Lock
from datetime import datetime
from chess import Board

from .base import GameEngine
from ..services.reset_time import next_reset_time


class ChessPuzzleEngine(GameEngine):
    """
    Board must be given in FEN.
    Player moves and solutions must be in UCI.
    """
    def __init__(self, fetcher):  # fetcher = lamba: provider(http)
        self._fetcher = fetcher
        self._lock = Lock()       # to prevent data races
        self.reset_time: datetime = datetime.min  # force 1st reset
        self.fen: str | None = None
        self.solution: list[str] | None = None


    async def ensure_daily_reset(self) -> bool:
        async with self._lock:
            if datetime.utcnow() >= self.reset_time:
                data = await self._fetcher()
                self.fen = data['fen']
                self.solution = data['solution']
                self.reset_time = next_reset_time()
                return True
            return False


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

