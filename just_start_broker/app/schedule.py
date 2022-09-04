from typing import Protocol

from fastapi import APIRouter, Depends

from just_start_broker.file_persistence import get_schedule_accessor
from just_start_broker.schemas import Schedule


class ScheduleAccessor(Protocol):
    def create(self, schedule: Schedule) -> None:
        pass

    def read(self) -> Schedule:
        pass


router = APIRouter(prefix="/schedule")


@router.post("/", response_model=Schedule)
def create_schedule(
    schedule: Schedule,
    accessor: ScheduleAccessor = Depends(get_schedule_accessor),
) -> Schedule:
    accessor.create(schedule)
    return schedule


@router.get("/", response_model=Schedule)
def read_schedule(
    accessor: ScheduleAccessor = Depends(get_schedule_accessor),
) -> Schedule:
    return accessor.read()
