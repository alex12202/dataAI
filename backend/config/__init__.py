import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

CODE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(CODE_DIR)

API_V1_STR = "/api/v1"

DEVELOPMENT = os.getenv("DEVELOPMENT", None)
STAGING = os.getenv("STAGING", None)
PRODUCTION = os.getenv("PRODUCTION", None)

SECRET_KEY = os.getenv("SECRET_KEY", "this-is-not-a-secret-key-make-it-secret")

origins_str = os.getenv("CORS_ORIGINS", "")
if origins_str:
    CORS_ORIGINS = origins_str.split(",")
else:
    CORS_ORIGINS = []

AZURE_AI_SEARCH_SERVICE = os.getenv(
    "AZURE_AI_SEARCH_SERVICE", "MISSING-AZURE_AI_SEARCH_SERVICE"
)
AZURE_AI_SEARCH_API_KEY = os.getenv(
    "AZURE_AI_SEARCH_API_KEY", "MISSING-AZURE_AI_SEARCH_API_KEY"
)
AZURE_AI_SEARCH_API_VERSION = os.getenv(
    "AZURE_AI_SEARCH_API_VERSION", "MISSING-AZURE_AI_SEARCH_API_VERSION"
)

MODEL_VERSION = os.getenv("MODEL_VERSION", "MISSING-MODEL_VERSION")

DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME", "MISSING-DEPLOYMENT_NAME")
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT", "MISSING-OPENAI_ENDPOINT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "MISSING-OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = os.getenv(
    "OPENAI_EMBEDDING_MODEL", "MISSING-OPENAI_EMBEDDING_MODEL"
)

CHATGPT_KEY = os.getenv("CHATGPT_KEY", "MISSING-CHATGPT_KEY")

DB_DSN = os.getenv("DB_DSN", "MISSING-DB_DSN")
DB_UID = os.getenv("DB_UID", "MISSING-DB_UID")
DB_PWD = os.getenv("DB_PWD", "MISSING-DB_PWD")
