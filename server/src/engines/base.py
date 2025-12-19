'''
Interface for hot-swappable games
'''
from abc import ABC, abstractmethod


class GameEngine(ABC):
    '''
    GameEngine follows the Singleton pattern and is user-state agonstic.
    User states are stored in GameStateCache.
    Class only holds session-wide truths like reset_time.
    '''
    @abstractmethod
    async def ensure_daily_reset(self) -> bool:
        '''
        Inits state at reset time every 24h.
        Returns True if it reseted.

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


