from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .router.bot_router import router as bot_router
from .config.db import connect_to_db, close_db_connection, pool

app = FastAPI(
    title="Housing Real Estate AI Agent",
    description="AI Agent for Housing Real Estate with LangGraph",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Custom Middleware to connect to DB if not connected
@app.middleware("http")
async def db_connection_middleware(request: Request, call_next):
    global pool
    if pool is None:
        from .config.db import connect_to_db
        await connect_to_db()
    response = await call_next(request)
    return response

# Include routers
app.include_router(bot_router, prefix="/ai", tags=["ai-agent"])

@app.get("/")
async def root():
    return {"message": "Housing Real Estate AI Agent API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
