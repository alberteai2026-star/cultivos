from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import include_all_routers
from app.core.config import settings
from app.core.errors import http_exception_handler, validation_exception_handler


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version=settings.app_version)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware('http')
    async def request_id_middleware(request: Request, call_next):
        request_id = request.headers.get('x-request-id') or str(uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers['x-request-id'] = request_id
        return response

    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    include_all_routers(app)
    return app


app = create_app()
