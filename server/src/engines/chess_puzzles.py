from .base import GameEngine
from typing import Dict, Any, List
from chess import Board

class ChessPuzzleEngine(GameEngine):
    """
    Chess Puzzle engine using chess.Board.
    Takes in FEN notation to init board, solutions and player moves are in uci.
    """
    def __init__(self, fen, solution: List[str]):
        self.fen = fen
        self.solution = solution

    def init_state(self) -> Dict[str, Any]:
        # score = no. successful turns
        return {
            "fen": self.fen,
            "moves": [],
            "score": 0,
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
        if i >= len(self.solution) or move != self.solution[i]:
            return {**state, 'is_gameover': True, 'is_won': False}

        # else correct
        board.push_uci(move)
        moves = state['moves'] + [move]
        score = i+1

        # check if last move
        if score == len(self.solution):
            return {
                "fen": board.fen(),
                "moves": moves,
                "score": score,
                "is_gameover": True,
                "is_won": True
            }
        # else continue
        return {
            "fen": board.fen(),
            "moves": moves,
            "score": score,
            "is_gameover": False,
            "is_won": False
        }

    def is_gameover(self, state: Dict[str, Any]) -> bool:
        return state['is_gameover']

    def is_won(self, state: Dict[str, Any]) -> bool:
        return state['is_won']

