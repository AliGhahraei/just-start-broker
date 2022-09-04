from datetime import datetime
from functools import total_ordering
from operator import eq, lt
from typing import Any, Callable

from pydantic import conlist, root_validator, validator
from pydantic.dataclasses import dataclass


@total_ordering  # type: ignore[arg-type]
@dataclass
class Event:
    type: str
    start: datetime
    end: datetime

    def __eq__(self, other: Any) -> bool:
        return self._compare(other, eq)

    def __lt__(self, other: Any) -> bool:
        return self._compare(other, lt)

    def _compare(
        self,
        other: Any,
        compare: Callable[[Any, Any], bool],
    ) -> bool:
        try:
            start, end = other.start, other.end
        except AttributeError:  # pragma: no cover
            return NotImplemented
        return compare(self.start, start) and compare(self.end, end)

    @root_validator
    def start_happens_before_end(cls, values: dict[str, Any]) -> dict[str, Any]:
        if not values["start"] < values["end"]:
            raise ValueError("start must happen before end")
        return values


@dataclass
class SortedEventsContainer:
    events: conlist(Event, min_items=1)  # type: ignore[valid-type]

    @validator("events")
    def events_are_sorted(cls, v: list[Event]) -> list[Event]:
        if sorted(v) != v:
            raise ValueError("Events are not sorted")
        return v


@dataclass
class Schedule(SortedEventsContainer):
    expiration: datetime
