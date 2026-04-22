from uuid import uuid4

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def _request_id_from_request(request: Request) -> str:
    return getattr(request.state, 'request_id', '') or request.headers.get('x-request-id') or str(uuid4())


def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    request_id = _request_id_from_request(request)
    code = f'http_{exc.status_code}'
    message = exc.detail if isinstance(exc.detail, str) else 'HTTP error'
    details = exc.detail if not isinstance(exc.detail, str) else None
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'request_id': request_id,
            'error': {
                'code': code,
                'message': message,
                'details': details,
            },
        },
    )


def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    request_id = _request_id_from_request(request)
    return JSONResponse(
        status_code=422,
        content={
            'request_id': request_id,
            'error': {
                'code': 'validation_error',
                'message': 'Validation error',
                'details': exc.errors(),
            },
        },
    )
