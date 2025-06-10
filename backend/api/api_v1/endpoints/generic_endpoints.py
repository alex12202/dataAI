import logging
from typing import Dict
from fastapi import APIRouter

from backend.decorators import log_endpoint

logger = logging.getLogger(__name__)

router = APIRouter()


# Ensure logging is properly configured
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@router.get("/health")
@log_endpoint
async def health_check() -> Dict[str, str]:
    """
    Performs a health check for the application.

    This endpoint is used to verify that the application is running and healthy.
    It returns a dictionary containing the status and a message indicating the
    health of the application.

    Returns:
        Dict[str, str]: A dictionary with the following keys:
            - "status": A string indicating the health status (e.g., "OK").
            - "message": A string providing additional information about the health status.
    """
    return {
        "status": "OK",
        "message": "Application is healthy",
    }
