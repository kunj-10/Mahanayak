from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Mhanayak API",
    description="Agentic-AI based environmentl event deive managar.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

origins = ["*"] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from app.api.routes import organiser_router
from app.api.routes.auth import router as auth_router

app.include_router(auth_router, prefix='/api/auth')
app.include_router(organiser_router, prefix="/api")


@app.get("/", tags=["health"])
async def root():
    """Root endpoint for API health check."""
    return {
        "status": "online",
        "app_name": "Mahanayak",
        "version": "0.1.0"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Run with: uvicorn app.main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 