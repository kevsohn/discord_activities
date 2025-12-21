# discord_activities

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


project/
├── shared/                     # Shared between front & backend
│   ├── __init__.py             
│   └── game_reg.py             # Game registry & specifications
|
├── client/                     # Frontend (React + Vite)
│   ├── index.html              # Single HTML entry point
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx            # App entry point
│       ├── App.jsx
│       ├── auth/               # Discord OAuth handling
│       │   └── discord.js      # login flow + token handling
│       ├── api/                # Frontend API wrappers
│       │   ├── auth.js
│       │   └── games.js
│       ├── games/              # Frontend adapters (hot-swappable)
│       │   ├── base.js         # GameAdapter interface
│       │   └── chess.js        # Chess adapter
│       └── components/         # Reusable React components
│           └── GameView.jsx    # Generic game renderer
│
├── server/                     # Backend (FastAPI)
│   ├── .env
│   ├── src/
│   │   ├── main.py             # App entry point (app.state)
│   │   ├── config.py
|   |   |
│   │   ├── api/                # FastAPI Routers
│   │   │   ├── auth.py         # Discord OAuth2 flow
│   │   │   ├── games.py        # Game logic
│   │   │   └── stats.py        # Player stats (for discord bot)
|   |   |
│   │   ├── engines/            # GameEngines (hot-swappable)
│   │   │   ├── base.py         # abstract class
│   │   │   ├── chess_puzzle.py
│   │   │   └── [others].py
|   |   |
│   │   ├── providers/          # Game data providers
│   │   │   ├── lichess.py
│   │   │   └── [others].py
│   │   |
│   │   ├── depends/            # Dependancies (for fastAPI Depends())
│   │   |   ├── engine_reg.py   # GameEngine & provider registry + alloc
│   │   |   ├── game_states.py  # GameStateStore interface
│   │   |   ├── sessions.py     # SessionManager & session ID
│   │   |   ├── streak.py       # Daily streak logic  
│   │   |   ├── redis.py        # Gets app.state.redis
│   │   |   └── http.py         # Gets app.state.http 
|   |   |
│   │   ├── services/           # Business-side logic 
│   │   |   ├── leaderboard.py  # Daily rankings logic  
│   │   |   ├── reset.py        # Daily reset logic (state TTL, game reset, stats)
│   │   │   ├── save.py         # Redis -> DB before reset 
│   │   |   └── error.py        # Wrapper for HTTPException
|   |   |
│   │   └── db/                 # asyncpg / sqlalchemy
│   │       ├── models/         # Alchemy models
│   │       └── queries/    
│   │
│   └── test/
│
├── README.md
└── requirements.txt

