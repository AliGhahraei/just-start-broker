from typing import Protocol, Type

from fastapi import Depends, FastAPI, Request
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse
from starlette.status import HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_ENTITY

from just_start_broker.file_persistence import get_schedule_accessor
from just_start_broker.persistence import ScheduleNotExpired, ScheduleNotFoundError
from just_start_broker.schemas import Schedule

CLIENT_ERRORS = {
    ScheduleNotExpired: HTTP_422_UNPROCESSABLE_ENTITY,
    ScheduleNotFoundError: HTTP_404_NOT_FOUND,
}
app = FastAPI()


class ScheduleAccessor(Protocol):
    def create(self, schedule: Schedule) -> None:
        pass

    def read(self) -> Schedule:
        pass


def register_handler(handled_type: Type[Exception], status: int) -> None:
    @app.exception_handler(handled_type)
    async def client_error_handler(_: Request, ex: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status,
            content=jsonable_encoder({"error": str(ex)}),
        )


for error_type, http_status in CLIENT_ERRORS.items():
    register_handler(error_type, http_status)


@app.post("/schedule", response_model=Schedule)
def create_schedule(
    schedule: Schedule,
    accessor: ScheduleAccessor = Depends(get_schedule_accessor),
) -> Schedule:
    accessor.create(schedule)
    return schedule


@app.get("/schedule", response_model=Schedule)
def read_schedule(
    accessor: ScheduleAccessor = Depends(get_schedule_accessor),
) -> Schedule:
    return accessor.read()
