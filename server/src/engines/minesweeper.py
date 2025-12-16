from .base import GameEngine
from typing import Dict, Any

class MinesweeperEngine(GameEngine):
    """
    """
    def init_state(self) -> Dict[str, Any]:
        pass

    def update_state(self, state: Dict[str, Any], action: Dict[str, Any]) -> Dict[str, Any]:
        pass

    def is_gameover(self, state: Dict[str, Any]) -> bool:
        pass

    def is_won(self, state: Dict[str, Any]) -> bool:
        pass

