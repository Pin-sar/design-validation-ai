from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings
from app.core.logging import logger
from app.core.storage import storage


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME)

    @app.on_event("startup")
    def _startup():
        storage.init_db()
        logger.info("Startup complete.")

    app.include_router(router, prefix="/v1")
    return app


app = create_app()
