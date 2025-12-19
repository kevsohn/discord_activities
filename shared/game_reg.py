'''
Hot-swappable discord activites.

The frontend and backend cannot choose
the appropriate schema and engine, respectively,
if the game name is not specified here.

When adding a new game, you MUST:
1) Register game name here
2) Add a GameEngine child in server/src/engines/
   to define game logic
3) Register game specs in server/src/depends/engine_registry.py
   following the outlined schema using the same game name and
   engine name
4) Add any provider modules (ex: if game calls an ext API to init)
   in server/src/services/
'''

GAMES = [
    'chess_puzzle',
    'minesweeper'
]
