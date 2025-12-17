from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.games.games import router as games_router

# --- Create app ---
app = FastAPI(title="Game Platform API")

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include routers ---
app.include_router(games_router)

# --- Optional startup / shutdown events ---
@app.on_event("startup")
async def startup_event():
    print("Server starting...")
    # Example: pre-fetch daily puzzles, connect DB, etc.

@app.on_event("shutdown")
async def shutdown_event():
    print("Server shutting down...")
    # Example: close DB connections, cleanup

