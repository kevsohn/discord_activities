Discordle: Hot-swappable daily Discord Activities puzzles.

To run server:
1) lsof -i:5432 and kill process if exists
2) docker run --name postgres \
    -e POSTGRES_USER=app \
    -e POSTGRES_PASSWORD=test123 \
    -e POSTGRES_DB=test_db \
    -p 5432:5432 \
    -d postgres:16
3) Check redis-cli works
4) Check if b_TEST is disabled in server/src/config.py
5) Goto server/ and run uvicorn src.main:app --reload

To run client:
1) npm run dev
2) cloudflared tunnel --url http://localhost:5173


When adding a new puzzle game, you MUST:
1) Register the game in shared/game_reg.json

2) Add a GameEngine child in server/src/engines/ to define game logic + register it in server/src/depends/engine_reg.py

3) Add any puzzle data provider modules in server/src/providers/

4) Add a GameRenderer component in client/src/components/renderers + register it in client/src/App.jsx 


Game Contract:
On server start, every GameEngine is loaded for all registered games. This means you can swap the selected game in the frontend without restarting the backend b/c every API call specifies the current game ID to differentiate.

The endpoints of api/games are /start, /update, and /house_turn. All games need to implement /start and /update; house_turn is optional and is automatically played after each player turn, if exists.

Each GameEngine instance is a singleton and thus needs to lock computation during daily resets. This is done thru the "ensure_reset" function inside each GameEngine but is tied to provider logic, so follow the example engine class when implementing.

Daily resets are coordinated in epochs (i.e. 2026/01/01, 2026/01/02, etc) and the default reset time is midnight UTC, which can be changed in config.py. Game states automatically expire at the end of every epoch (Redis TTL) so they are not persisted to the DB; only player stats are persisted.

Stats are persisted NOT immediately after the epoch rolls over but when the 1st player of the day starts a game. The leaderboard is updated every update call, providing live rankings, and is not reset or persisted until the same condition is met.


project/
├── shared/                     # Shared between front & backend
│   └── game_reg.json           # Game registry
|
├── client/                     # Frontend (React + Vite)
│   ├── index.html              
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx                # App entry point
│       ├── App.jsx                 # Auth + render game
│       ├── config.js               # Get current game ID
|       |
│       ├── components/             # React components
│       |   ├── LoadingScreen.jsx
│       |   ├── ErrorBoundary.jsx   # Rendering error handler
│       |   ├── GameWrapper.jsx     # Game state handler (sequencing, resets, errors)
│       |   └── renderers           # Game UIs
|       |       ├── ChessPuzzle.jsx 
|       |       └── [others].jsx 
|       |
│       └── services/           
│           ├── Auth.js             # Discord OAuth2 flow
│           ├── SessionManager.js   # Create sesh + maintain heartbeat
│           └── GameAPI.js          # Backend interface for game state
│
|
├── server/                     # Backend (FastAPI + Redis + Postgres)
│   ├── .env
│   ├── src/
│   │   ├── __init__.py     
│   │   ├── main.py             # App entry point + engine alloc
│   │   ├── config.py
|   |   |
│   │   ├── api/                # FastAPI Routers
│   │   │   ├── auth.py         # Discord OAuth2 flow
│   │   │   ├── games.py        # Game state access logic
│   │   │   └── stats.py        # Player stats (for discord bot)
|   |   |
│   │   ├── engines/            # GameEngines (hot-swappable)
│   │   │   ├── base.py         # abstract class
│   │   │   ├── chess_puzzle.py
│   │   │   └── [others].py
|   |   |
│   │   ├── providers/          # Puzzle data providers
│   │   │   ├── lichess.py      # Chess puzzle API
│   │   │   └── [others].py
│   │   |
│   │   ├── depends/            # Dependancies (for fastAPI Depends())
│   │   |   ├── engine_reg.py   # GameEngine & provider registry
│   │   |   ├── game_states.py  # GameStateStore manager
│   │   |   ├── sessions.py     # SessionManager & session ID
│   │   |   ├── streak.py       # Daily streak logic  
│   │   |   ├── db_session.py   # Gets app.state.db_session  
│   │   |   ├── redis.py        # Gets app.state.redis
│   │   |   └── http.py         # Gets app.state.http 
|   |   |
│   │   ├── services/           
│   │   |   ├── leaderboard.py  # Daily rankings logic  
│   │   |   ├── reset.py        # Daily reset logic (state TTL, game reset, stats)
│   │   │   ├── save.py         # Redis -> DB before reset 
│   │   |   └── error.py        # Wrapper for HTTPException
|   |   |
│   │   └── db/                 # asyncpg / sqlalchemy
│   │       └── models/         # Alchemy models
│   │           └── stats.py    
│   │
│   └── test/
│
├── README.md
└── requirements.txt


Design Diagram:
┌──────────────────────────┐
│        Browser           │
│     (React + Vite)       │
│                          │
│  ┌──────────────────┐    │
│  │ Discord Activity │◀───┼── Discord OAuth2
|  | Launch           |    |
│  └──────────────────┘    │
│          │               │
│          ▼               │
│  ┌──────────────────┐    │
│  │ Game UI          │    │
│  │ (React)          │    │
│  └──────────────────┘    │
│          │               │
│          ▼               │
│  ┌──────────────────┐    │
│  │ API Client       │────┼── Authenticated HTTP Requests (session)
│  └──────────────────┘    │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│        FastAPI           │
│   (Backend / API Server) │
│                          │
│  ┌──────────────────┐    │
│  │ Auth Routes      │◀───┼── Discord OAuth2
│  └──────────────────┘    │
│          │               │
│          ▼               │
│  ┌──────────────────┐    │
│  │ User Context     │    │
│  │ (session)        │    │
│  └──────────────────┘    │
│          │               │
│          ▼               │
│  ┌──────────────────┐    │
│  │ Game Routes      │    │
│  │ (API endpoints)  │    │
│  └──────────────────┘    │
│          │               │
│          ▼               │
│  ┌──────────────────┐    │
│  │ Game Engine      │    │
│  │ Interface (base) │    │
│  │ Chess / Other    │    │
│  └──────────────────┘    │
│          │               │
│          ▼               │
│  ┌──────────────────┐    │
│  │ PostgreSQL       │    │
│  │ Users / Stats    │    │
│  └──────────────────┘    │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Discord Bot             │
│                          │
│  - Posts rankings        │
│    (every 24h)           │
│  - Uses service account  │
│    (no user OAuth)       │
└──────────────────────────┘
