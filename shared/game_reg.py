'''
Hot-swappable discord activites.

The frontend and backend cannot choose
the appropriate schema and engine, respectively,
if the game name is not specified here.

When adding a new game, you MUST:
1) Register game name here
2) Add a GameEngine child in server/src/engines/
   to define game logic
3) Register game specs in server/src/depends/engine_reg.py
   following the outlined schema
4) Add any provider modules (i.e. Ext API calls for init data)
   in server/src/providers/
'''

GAMES = [
    'chess_puzzle',
    'minesweeper'
]
