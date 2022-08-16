from datetime import datetime

from just_start_broker.schemas import Event, SortedEventsContainer

from pytest import fixture, mark, raises


class TestEvent:
    @staticmethod
    @mark.parametrize('end', [datetime(2022, 8, 15, 23), datetime(2022, 8, 16)])
    def test_init_raises_value_error_if_start_is_not_before_end(end: datetime) -> None:
        with raises(ValueError, match="start must happen before end"):
            Event("Work", datetime(2022, 8, 16), end)


class TestSortedEventsContainer:
    @staticmethod
    @fixture
    def smaller_event() -> Event:
        return Event("Work", datetime(2022, 8, 16), datetime(2022, 8, 16, 1))

    @staticmethod
    @fixture
    def bigger_event() -> Event:
        return Event("Gym", datetime(2022, 8, 16, 1), datetime(2022, 8, 16, 2))

    @staticmethod
    def test_init_raises_value_error_if_events_are_unsorted(
        smaller_event: Event,
        bigger_event: Event,
    ) -> None:
        with raises(ValueError, match="Events are not sorted"):
            SortedEventsContainer([bigger_event, smaller_event])

    @staticmethod
    def test_init_creates_if_args_are_valid(
        smaller_event: Event,
        bigger_event: Event,
    ) -> None:
        SortedEventsContainer([smaller_event, bigger_event])
