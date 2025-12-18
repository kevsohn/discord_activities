from typing import Dict, Any
from chess import Board

from .base import GameEngine
from ..services.lichess import fetch_daily_puzzle


class ChessPuzzleEngine(GameEngine):
    """
    Takes in FEN to init board, solutions and player moves are in UCI.
    """
    def __init__(self):
        self.fen = None
        self.solution = None
        self.max_score = 0


    async def setup(self, http):
        data = await fetch_daily_puzzle(http)
        self.fen = data['fen']
        self.solution = data['solution']
        self.max_score = len(self.solution)


    def init_state(self) -> Dict[str, Any]:
        return {
            "fen": self.fen,
            "moves": [],
            "score": 0,            # no. successful turns
            "is_gameover": False,
            "is_won": False
        }


    def update_state(self, state: Dict[str, Any], action: Dict[str, Any]) -> Dict[str, Any]:
        if state['is_gameover']:
            return state

        board = Board(state["fen"])
        move = action["uci"]
        i = len(state['moves'])  # i lags behind turn by 1 since new move hasnt been added yet

        # if wrong move, gameover
        if i >= self.max_score or move != self.solution[i]:
            return {**state, 'is_gameover': True, 'is_won': False}

        # else correct
        board.push_uci(move)
        new_moves = state['moves'] + [move]
        new_score = i+1

        # check if last move
        if new_score == self.max_score:
            return {
                "fen": board.fen(),
                "moves": new_moves,
                "score": new_score,
                "is_gameover": True,
                "is_won": True
            }
        # else continue
        return {
            "fen": board.fen(),
            "moves": new_moves,
            "score": new_score,
            "is_gameover": False,
            "is_won": False
        }


    def is_gameover(self, state: Dict[str, Any]) -> bool:
        return state['is_gameover']


    def is_won(self, state: Dict[str, Any]) -> bool:
        return state['is_won']


    def get_max_score() -> int:
        return self.max_score

