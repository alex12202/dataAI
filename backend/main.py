import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from semantic_kernel.utils.logging import setup_logging
from starlette.middleware.sessions import SessionMiddleware

from backend import config
from backend.api.api_v1.routers import api_router
from backend.decorators import log_endpoint
from backend.session_context import lifespan

API_V1_STR = "/api/v1"

# Set up logging for the kernel
setup_logging()

# Ensure logging is properly configured
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Set up logging for the kernel
setup_logging()
logging.getLogger("kernel").setLevel(logging.DEBUG)

app = FastAPI(
    title="University Ai DEMO",
    openapi_url=f"{API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redocs",
    lifespan=lifespan,
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add the Session Middleware
app.add_middleware(
    SessionMiddleware, secret_key=config.SECRET_KEY, max_age=3600  # 1 hour
)

# Include routers
app.include_router(api_router, prefix=API_V1_STR)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)
