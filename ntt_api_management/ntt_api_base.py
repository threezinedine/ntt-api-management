from abc import ABCMeta
from datetime import datetime
from .i_ntt_api import *


class NTTAPIBase(INTTAPI):
    def __init__(
        self,
        key: str,
        last_request_time: datetime = datetime.now(),
    ) -> None:
        self.__key = key
        self.__last_request_time = last_request_time

    @property
    def key(self) -> str:
        return self.__key

    @property
    def last_request_time(self) -> datetime:
        return self.__last_request_time

    @last_request_time.setter
    def last_request_time(self, value: datetime) -> None:
        self.__last_request_time = value

    def make_request(self, **kwargs) -> None:
        self.__last_request_time = datetime.now()
        self._make_request(**kwargs)

    @abstractmethod
    def _make_request(self, **kwargs) -> None:
        pass

    def ToDict(self) -> dict[str, object]:
        return {
            "key": self.key,
            "last_request_time": self.__last_request_time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def FromDict(self, data: dict[str, object]) -> INTTAPI:
        self._PreprocessIncomingDict(data)
        self._FromDict(data)
        return self

    def _FromDict(self, data: dict[str, object]) -> None:
        self.__key = data["key"]
        self.__last_request_time = data["last_request_time"]

    def _PreprocessIncomingDict(self, data: dict[str, object]) -> None:
        data["last_request_time"] = datetime.strptime(
            data["last_request_time"], "%Y-%m-%d %H:%M:%S"
        )

    def should_reset(self) -> bool:
        return False

    def reset(self) -> None:
        pass

    def __repr__(self) -> str:
        return f"<NTT API: {self.key} />"
