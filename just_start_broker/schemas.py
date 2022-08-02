from datetime import date, time

from pydantic import conlist
from pydantic.dataclasses import dataclass


@dataclass
class Event:
    type: str
    start: time
    end: time


@dataclass
class Schedule:
    date: date
    events: conlist(Event, min_items=1)  # type: ignore[valid-type]
