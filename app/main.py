from fastapi import FastAPI

from app.routers import pull_requests, repositories

app = FastAPI(
    title="GitHub Client API",
    description="A REST API to interact with GitHub repositories and pull requests",
    version="1.0.0",
)

app.include_router(repositories.router)
app.include_router(pull_requests.router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
