from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, llm
from app.database import close_db_connection

app = FastAPI(title="LLM Project API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(llm.router, prefix="/api/llm", tags=["llm"])

@app.get("/")
async def root():
    return {"message": "LLM Project API is running"}

@app.on_event("shutdown")
async def shutdown_event():
    await close_db_connection()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)