from abc import ABC, abstractmethod
from datetime import datetime


class INTTAPI(ABC):
    @abstractmethod
    def ToDict(self) -> dict[str, object]:
        pass

    @abstractmethod
    def FromDict(self, data: dict[str, object]) -> "INTTAPI":
        pass

    @abstractmethod
    def make_request(self, **kwargs) -> None:
        pass

    @abstractmethod
    def can_be_used(self) -> bool:
        pass

    @abstractmethod
    def should_reset(self) -> bool:
        pass

    @abstractmethod
    def reset(self) -> None:
        pass

    @property
    @abstractmethod
    def key(self) -> str:
        pass

    @property
    @abstractmethod
    def last_request_time(self) -> datetime:
        pass

    @last_request_time.setter
    @abstractmethod
    def last_request_time(self, value: datetime) -> None:
        pass
