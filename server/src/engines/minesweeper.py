'''
Read engines/base.py for info.
'''
import asyncio

from .base import GameEngine


class MinesweeperEngine(GameEngine):
    """
    """
    def __init__(self):
        super().__init__()
        self.ndim: int = 8
        self.mines: list | None = None


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
            # else is next epoch so new seed
            self.mines = self.init_mines()
            self._epoch = cur_epoch
            return True


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
        return len(self.mines)


    def init_mines(self):
        '''Randomly scatters mines across grid'''
        return []


