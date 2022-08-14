from datetime import datetime

from pydantic import conlist
from pydantic.dataclasses import dataclass


@dataclass
class Event:
    type: str
    start: datetime
    end: datetime


@dataclass
class Schedule:
    expiration: datetime
    events: conlist(Event, min_items=1)  # type: ignore[valid-type]
