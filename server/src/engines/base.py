from abc import ABC, abstractmethod
from typing import Any, Dict

class GameEngine(ABC):
    '''Interface for hot-swappable games'''

    @abstractmethod
    def init_state(self) -> Dict[str, Any]:
        '''
        Returns game's init state as a JSON-serializable dict
        '''
        pass

    @abstractmethod
    def update_state(self, state: Dict[str, Any], action: Dict[str, Any]) -> Dict[str, Any]:
        '''
        Applies a player action to game state
        Returns state and optional flags:
        {
            "state": {...},
            "score": int,
            "is_gameover: bool",
            "is_won: bool"
        }
        '''
        pass

    @abstractmethod
    def is_gameover(self, state: Dict[str, Any]) -> bool:
        """Returns True if game has ended (success or fail)"""
        pass

    @abstractmethod
    def is_won(self, state: Dict[str, Any]) -> bool:
        """Returns True if the player has won"""
        pass
