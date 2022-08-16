from datetime import datetime

from just_start_broker import JustStartBrokerException


class ScheduleNotExpired(JustStartBrokerException):
    def __init__(self, expiration: datetime):
        self.expiration = expiration

    def __str__(self) -> str:
        return f"Cannot set a new schedule until {self.expiration}"


class ScheduleNotFoundError(JustStartBrokerException):
    def __str__(self) -> str:
        return "Schedule did not exist"
