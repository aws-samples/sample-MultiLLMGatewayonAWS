from contextlib import asynccontextmanager
from fastapi import FastAPI
from ..api.routes import router
from .handler import handler
import logging
from fastapi.middleware.cors import CORSMiddleware

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application"""
    # Startup
    yield
    # Shutdown
    await handler.close()

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    # Initialize FastAPI app with lifespan handler
    app = FastAPI(lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  
        allow_methods=["*"],     
        allow_headers=["*"],     
    )
    # Include API routes
    app.include_router(router)

    return app

# Create the application instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug", log_config="log_conf.yaml")
