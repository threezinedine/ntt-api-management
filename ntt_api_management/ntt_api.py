from datetime import datetime


class NTTAPI:
    def __init__(
        self,
        key: str = "",
        number_requests: int = 0,
        last_request_time: datetime = datetime.now(),
    ) -> None:
        self.__key = key
        self.__number_requests = number_requests
        self.__last_request_time = last_request_time

    @property
    def key(self) -> str:
        return self.__key

    @property
    def number_requests(self) -> int:
        return self.__number_requests

    @number_requests.setter
    def number_requests(self, value: int) -> None:
        self.__number_requests = value

    @property
    def last_request_time(self) -> datetime:
        return self.__last_request_time

    @last_request_time.setter
    def last_request_time(self, value: datetime) -> None:
        self.__last_request_time = value

    def ToDict(self) -> dict[str, object]:
        return {
            "key": self.__key,
            "number_requests": self.__number_requests,
            "last_request_time": self.__last_request_time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def FromDict(data: dict[str, object]) -> "NTTAPI":
        if "last_request_time" not in data:
            data["last_request_time"] = datetime.now()
        else:
            data["last_request_time"] = datetime.strptime(
                data["last_request_time"], "%Y-%m-%d %H:%M:%S"
            )
        return NTTAPI(**data)

    def __repr__(self) -> str:
        return f"<NTT API: {self.key} - Requests: {self.number_requests} Last Request: {self.last_request_time}/>"
