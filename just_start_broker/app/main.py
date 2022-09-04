from typing import Type

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse
from starlette.status import HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_ENTITY

from just_start_broker import ClientError, EntityNotFoundError
from just_start_broker.app import schedule


CLIENT_ERRORS = {
    ClientError: HTTP_422_UNPROCESSABLE_ENTITY,
    EntityNotFoundError: HTTP_404_NOT_FOUND,
}

app = FastAPI()
app.include_router(schedule.router)


def register_handler(handled_type: Type[Exception], status: int) -> None:
    @app.exception_handler(handled_type)
    async def client_error_handler(_: Request, ex: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status,
            content=jsonable_encoder({"error": str(ex)}),
        )


for error_type, http_status in CLIENT_ERRORS.items():
    register_handler(error_type, http_status)
