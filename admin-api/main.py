from fastapi import FastAPI

from routes.books import books_route
from routes.health import health_route
from routes.users import users_route
from utils.constants import DOCS_URL
from utils.dependency_container import get_container
from utils.environment import APP_ENVIRONMENT
from utils.logger_utility import getlogger
from utils.lifespan_utility import lifecycle_manager

logger = getlogger("uvicorn")
logger.info(f"Environment: {APP_ENVIRONMENT}")
requestlogger = getlogger(name="uvicorn.access")

app = FastAPI(
    title="Library Admin API", openapi_url=DOCS_URL, lifespan=lifecycle_manager
)

app.state.ioc_container = get_container()

app.include_router(books_route, prefix="/api")
app.include_router(users_route, prefix="/api")
app.include_router(health_route)
