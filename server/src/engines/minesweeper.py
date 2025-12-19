'''
Read engines/base.py for info.
'''
from asyncio import Lock
from datetime import datetime

from .base import GameEngine
from ..services.reset_time import next_reset_time


class MinesweeperEngine(GameEngine):
    """
    """
    def __init__(self):
        self._lock = Lock()  # to prevent data races
        self.reset_time: datetime = datetime.min  # force 1st reset
        self.ndim = 8
        self.max_score = 0


    async def ensure_daily_reset(self) -> bool:
        async with self._lock:
            if datetime.utcnow() >= self.reset_time:
                self.reset_time = next_reset_time()
                return True
            return False


    def get_init_state(self) -> dict:
        mines = self.init_mines()
        self.max_score = len(mines)
        return {
            "mines": mines,
            "seen_tiles": [],
            "score": 0,         # no. mines correctly revealed
            "gameover": False,
            "won": False
        }


    def update_state(self, state: dict, action: dict) -> dict:
        if state['gameover']:
            return state

        score = state['score']
        seen_tiles = state['seen_tiles']

        # cont
        return {
            "mines": state['mines'],
            "seen_tiles": seen_tiles,
            "score": score,
            "gameover": False,
            "won": False
        }


    def get_max_score(self) -> int:
        return self.max_score


    def init_mines(self):
        '''Randomly scatters mines across grid'''
        return []


