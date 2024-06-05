from abc import ABC, abstractmethod


class INTTAPI(ABC):
    @abstractmethod
    def ToDict(self) -> dict[str, object]:
        pass

    @staticmethod
    @abstractmethod
    def FromDict(data: dict[str, object]) -> "INTTAPI":
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
