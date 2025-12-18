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
│   │   ├── main.py             # App entry point
│   │   ├── config.py           # Imported env vars
│   │   ├── db.py               # DB conn/SQLAlchemy setup
|   |   |
│   │   ├── engines/            # Game engines (hot-swappable)
│   │   │   ├── base.py         # GameEngine interface
│   │   │   ├── chess_puzzles.py
│   │   │   └── [other_games].py
|   |   |
│   │   ├── api/                # FastAPI routers
│   │   │   ├── games/          # Game logic
│   │   │   │   ├── routes.py
│   │   │   │   └── schemas.py  # Pydantic models
│   │   │   ├── auth/           # OAuth2 flow
│   │   │   │   ├── routes.py
│   │   │   │   └── schemas.py
│   │   │   └── stats/          # Player stats for discord bot
│   │   │       ├── routes.py
│   │   │       └── schemas.py
|   |   |
│   │   ├── services/           # Backend-only APIs
│   │   │   ├── sessions.py     # Creates/del seshes
│   │   │   ├── error.py        # Wrapper for HTTPException
│   │   │   └── lichess.py
│   │   |
│   │   ├── depends/               # Dependancies (used by fastAPI w/ Depends)
│   │       ├── session.py      # Gets any sesh-related data
│   │       ├── http.py         # Gets app.state.http 
│   │       └── redis.py        # Gets app.state.redis
│   │
│   └── test/
│       ├── [tests].py
│
├── shared/                     # Shared between front & backend
│   ├── __init__.py             
│   └── game_specs.py           # Game specifications
│
├── README.md
└── requirements.txt

