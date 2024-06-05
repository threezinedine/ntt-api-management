from datetime import datetime, timedelta, date
from .i_ntt_api import INTTAPI


class NTTAPIDailyLimit(INTTAPI):
    daily_limit = 10

    def __init__(
        self,
        key: str = "",
        number_requests: int = 0,
        last_access: date = date.today(),
    ) -> None:
        self.__key = key
        self.__number_requests = number_requests
        self.__last_access = last_access

    @property
    def key(self) -> str:
        return self.__key

    # just for testing purposes, not used in the real implementation
    @property
    def number_requests(self) -> int:
        return self.__number_requests

    @property
    def last_access(self) -> date:
        return self.__last_access

    @last_access.setter
    def last_access(self, value: date) -> None:
        self.__last_access = value

    # end of testing purposes

    def make_request(self, **kwargs) -> None:
        self.__number_requests += 1

    def ToDict(self) -> dict[str, object]:
        return {
            "key": self.__key,
            "number_requests": self.__number_requests,
            "last_access": self.__last_access.strftime("%Y-%m-%d"),
        }

    def FromDict(data: dict[str, object]) -> "INTTAPI":
        data["last_access"] = datetime.strptime(data["last_access"], "%Y-%m-%d").date()
        return NTTAPIDailyLimit(**data)

    def can_be_used(self) -> bool:
        return self.__number_requests < NTTAPIDailyLimit.daily_limit

    def should_reset(self) -> bool:
        return self.__last_access != date.today()

    def reset(self) -> None:
        self.__number_requests = 0
        self.__last_access = date.today()

    def __repr__(self) -> str:
        return f"<NTT API: {self.key} - Requests: {self.number_requests} />"


class NTTAPIMinuteLimit(INTTAPI):
    def __init__(
        self,
        key: str = "",
        request_times: int = 0,
        last_request_time: datetime = datetime.now(),
    ) -> None:
        self.__key = key
        self.__request_times = request_times
        self.__last_request_time: datetime = last_request_time

    @property
    def key(self) -> str:
        return self.__key

    @property
    def number_requests(self) -> int:
        return self.__request_times

    # just for testing purposes, not used in the real implementation
    @property
    def last_request_time(self) -> datetime:
        return self.__last_request_time

    @last_request_time.setter
    def last_request_time(self, value: datetime) -> None:
        self.__last_request_time = value

    # end of testing purposes

    def make_request(self, **kwargs) -> None:
        self.__last_request_time = datetime.now()
        self.__request_times += 1

    def can_be_used(self) -> bool:
        if self.__request_times == 0:
            return True
        elif self.__last_request_time < datetime.now() - timedelta(minutes=1):
            return True
        else:
            return False

    def ToDict(self) -> dict[str, object]:
        return {
            "key": self.__key,
            "request_times": self.__request_times,
            "last_request_time": self.__last_request_time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    @staticmethod
    def FromDict(data: dict[str, object]) -> INTTAPI:
        data["last_request_time"] = datetime.strptime(
            data["last_request_time"], "%Y-%m-%d %H:%M:%S"
        )

        return NTTAPIMinuteLimit(**data)

    def should_reset(self) -> bool:
        return False

    def reset(self) -> None:
        pass
