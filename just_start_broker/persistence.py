from datetime import datetime

from just_start_broker import ClientError, EntityNotFoundError


class ScheduleNotExpired(ClientError):
    def __init__(self, expiration: datetime):
        self.expiration = expiration

    def __str__(self) -> str:
        return f"Cannot set a new schedule until {self.expiration}"


class ScheduleNotFoundError(EntityNotFoundError):
    def __str__(self) -> str:
        return "Schedule did not exist"
