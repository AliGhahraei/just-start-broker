from datetime import datetime

from just_start_broker.schemas import Event, Schedule

from pytest import fixture


@fixture
def schedule() -> Schedule:
    return Schedule(
        expiration=datetime(2022, 8, 15),
        events=[
            Event(
                "Work",
                datetime(2022, 8, 14, 3),
                datetime(2022, 8, 14, 4),
            )
        ],
    )
