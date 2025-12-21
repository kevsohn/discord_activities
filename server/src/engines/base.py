'''
Interface for hot-swappable games
'''
from abc import ABC, abstractmethod
import asyncio


class GameEngine(ABC):
    '''
    GameEngine follows the Singleton pattern and is user-state agonstic.
    User states are stored in GameStateStore.
    Class only holds truths shared by all players, like solution.
    '''
    def __init__(self, game_id: str):
        self._game_id = game_id
        self._lock = asyncio.Lock()  # to prevent data races
        self._epoch: str | None = None


    @abstractmethod
    async def ensure_reset(self, cur_epoch: str) -> bool:
        '''
        Resets game state if self.epoch != cur_epoch.
        Returns True if it reset.

        Some games fetch init data here using
        fetcher = lambda: provider(http_client).
        '''
        pass


    @abstractmethod
    def get_init_state(self) -> dict:
        '''
        Returns game's init state as a JSON-serializable dict.
        state = {
            "board": list,
            "score": int,
            "gameover: bool",
            "won: bool"
        }
        '''
        pass


    @abstractmethod
    def update_state(self, state: dict, action: dict) -> dict:
        '''Applies player action and returns updated state.'''
        pass


    @abstractmethod
    def get_max_score(self) -> int:
        '''Returns max score for display and ranking purposes'''
        pass


