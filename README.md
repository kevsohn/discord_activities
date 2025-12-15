# discord_activities

Design Diagram:
┌──────────────────────────┐
│        Browser           │
│  (React + Discord OAuth) │
│                          │
│  ┌──────────────────┐    │
│  │ Discord OAuth    │◀───┼── User Login
│  └──────────────────┘    │
│          │               │
│          ▼               │
│  ┌──────────────────┐    │
│  │ Game View        │    │
│  │ (React)          │    │
│  └──────────────────┘    │
│          │               │
│          ▼               │
│  ┌──────────────────┐    │
│  │ API Client       │───┼── Authenticated HTTP Requests (JWT)
│  └──────────────────┘    │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│        FastAPI           │
│   (Backend / API Server) │
│                          │
│  ┌──────────────────┐    │
│  │ Auth Routes      │◀───┼── Discord OAuth
│  └──────────────────┘    │
│          │               │
│          ▼               │
│  ┌──────────────────┐    │
│  │ User Context     │    │
│  │ (JWT / session)  │    │
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
│  Discord Bot (Worker)    │
│                          │
│  - Polls /api/stats      │
│    (every 1h)            │
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
│   ├── app/
│   │   ├── main.py             # FastAPI app entry point
│   │   ├── db.py               # DB connection / SQLAlchemy setup
│   │   ├── models.py           # SQLAlchemy models
│   │   ├── config.py           # Env variables, secrets
│   │
│   │   ├── auth/               # Discord OAuth
│   │   │   ├── routes.py       # OAuth endpoints
│   │   │   ├── service.py      # Token validation, JWT creation
│   │   │   └── schemas.py
│   │   │
│   │   ├── api/                # FastAPI routers
│   │   │   ├── games/          # Game-related endpoints
│   │   │   │   ├── routes.py
│   │   │   │   ├── service.py  # Business logic / GameEngine calls
│   │   │   │   └── schemas.py  # Pydantic models for request/response
│   │   │   └── player_stats/   # Player stats API
│   │   │       ├── routes.py
│   │   │       └── schemas.py
│   │   │
│   │   ├── games/              # Backend game engines (hot-swappable)
│   │   │   ├── base.py         # GameEngine interface
│   │   │   └── chess.py        # Chess engine implementation
│   │   │   └── [other_games].py
│   │   │
│   │   └── utils/              # Helper functions
│   │       └── [e.g., scoring, state validation]
│   │
│   └── tests/                  # Backend unit / integration tests
│       ├── test_games.py
│       └── test_api.py
│
├── bot/                        # Discord bot for leaderboard updates
│   ├── main.py                 # Polling + posting rankings
│   └── config.py               # Bot token, channel, schedule settings
│
├── shared/                     # Shared contracts / docs
│   └── game_contract.md        # Game state/action/schema specification
│
├── .env                        # Environment variables (local dev)
├── README.md
└── requirements.txt            # Backend dependencies

