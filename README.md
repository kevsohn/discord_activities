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
│  - Resets stats          │
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
│   ├── src/
│   │   ├── main.py             # App entry point
│   │   ├── config.py           # Game selection and env vars
│   │   ├── redis.py            # Sessions & leaderboard
│   │   ├── db.py               # DB conn/SQLAlchemy setup
|   |   |
│   │   ├── engines/            # Game engines (hot-swappable)
│   │   │   ├── base.py         # GameEngine interface
│   │   │   └── chess_puzzles.py
│   │   │   └── [other_games].py
|   |   |
│   │   ├── api/                # FastAPI routers
│   │   │   ├── games/          # Game logic
│   │   │   │   ├── routes.py
│   │   │   │   └── schemas.py  # Pydantic models
│   │   │   ├── auth/           # Discord OAuth2
│   │   │   │   ├── routes.py
│   │   │   │   └── schemas.py
│   │   │   └── stats/          # Player stats
│   │   │       ├── routes.py
│   │   │       └── schemas.py
|   |   |
│   │   ├── services/           # Backend-only APIs
│   │   │   ├── sessions.py
│   │   │   ├── lichess.py
│   │
│   └── test/
│       ├── [tests].py
│
├── bot/                        # Discord bot for leaderboard updates
│   ├── main.py                 # Bot entry point
│   └── config.py               # Token, cmd prefix, etc
│
├── shared/                     # Shared contracts / docs
│   └── game_contract.md        # Game state/action/schema specification
│
├── .env                        # Environment variables (local dev)
├── README.md
└── requirements.txt            # Backend dependencies

