from typing import Protocol

from fastapi import Depends, FastAPI, Request
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from just_start_broker.file_persistence import get_schedule_accessor
from just_start_broker.persistence import ScheduleNotExpired
from just_start_broker.schemas import Schedule

CLIENT_ERRORS = [ScheduleNotExpired]
app = FastAPI()


class ScheduleAccessor(Protocol):
    def create(self, schedule: Schedule) -> None:
        pass


for error_type in CLIENT_ERRORS:

    @app.exception_handler(error_type)
    async def client_error_handler(_: Request, ex: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({"error": str(ex)}),
        )


@app.post("/schedule", response_model=Schedule)
def create_schedule(
    schedule: Schedule,
    accessor: ScheduleAccessor = Depends(get_schedule_accessor),
) -> Schedule:
    accessor.create(schedule)
    return schedule
