from abc import ABC, abstractmethod


class INTTAPI(ABC):
    @abstractmethod
    def ToDict(self) -> dict[str, object]:
        pass

    @abstractmethod
    def FromDict(data: dict[str, object]) -> "INTTAPI":
        pass

    @abstractmethod
    def make_request(**kwargs) -> None:
        pass

    @abstractmethod
    def can_be_used() -> bool:
        pass

    @property
    @abstractmethod
    def key(self) -> str:
        pass
