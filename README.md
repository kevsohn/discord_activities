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
│   │   ├── main.py             # App entry point (redis, db, etc)
│   │   ├── config.py           # .env vars
│   │   ├── db.py               # DB conn / SQLAlchemy setup
|   |   |
│   │   ├── api/                # FastAPI routers
│   │   │   ├── games.py        # Game logic
│   │   │   ├── auth.py         # OAuth2 flow
│   │   │   └── leaderboard.py  # Player stats for discord bot
|   |   |
│   │   ├── engines/            # Game engines (hot-swappable)
│   │   │   ├── base.py         # GameEngine interface
│   │   │   ├── chess_puzzle.py
│   │   │   └── [others].py
|   |   |
│   │   ├── providers/          # Game data providers
│   │   │   ├── lichess.py
│   │   │   └── [others].py
│   │   |
│   │   ├── depends/            # Dependancies (used by fastAPI w/ Depends)
│   │   |   ├── engine_reg.py   # Engine & provider registry & alloc
│   │   |   ├── session.py      # SessionManager & ID
│   │   |   ├── game_state.py   # GameStateCache interface
│   │   |   ├── http.py         # Gets app.state.http 
│   │   |   └── redis.py        # Gets app.state.redis
|   |   |
│   │   └── services/           # Backend-only APIs
│   │       ├── reset_time.py   # Returns daily reset time
│   │       └── error.py        # Wrapper for HTTPException
│   │
│   └── test/
│
├── shared/                     # Shared between front & backend
│   ├── __init__.py             
│   └── game_reg.py             # Game registry & specifications
│
├── README.md
└── requirements.txt

