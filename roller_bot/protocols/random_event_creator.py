from typing import Protocol, TypeVar

from roller_bot.protocols.random_event import RandomEvent

T = TypeVar("T", bound=RandomEvent)


class RandomEventCreator(Protocol[T]):
    def create(self) -> T:
        ...
