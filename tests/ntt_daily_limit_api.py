from ntt_api_management import *
from datetime import time, date, timedelta, datetime


class NTTAPIDailyLimit(NTTAPIBase):
    def __init__(
        self,
        key: str = "",
        number_requests: int = 0,
        request_limit: int = 100,
        last_request_time: datetime = datetime.now(),
    ) -> None:
        super().__init__(key, last_request_time)
        self.__number_requests = number_requests
        self.__request_limit = request_limit

    # just for testing purposes, not used in the real implementation
    @property
    def number_requests(self) -> int:
        return self.__number_requests

    @property
    def request_limit(self) -> int:
        return self.__request_limit

    @property
    def last_access(self) -> date:
        return self.last_request_time.date()

    @last_access.setter
    def last_access(self, value: date) -> None:
        self.last_request_time = datetime.combine(value, time.min)

    # end of testing purposes

    def _make_request(self, **kwargs) -> None:
        super()._make_request(**kwargs)
        self.__number_requests += 1

    def ToDict(self) -> dict[str, object]:
        baseDict = super().ToDict()
        baseDict["number_requests"] = self.__number_requests
        baseDict["request_limit"] = self.__request_limit

        return baseDict

    def _PreprocessIncomingDict(self, data: dict[str, object]) -> None:
        super()._PreprocessIncomingDict(data)

    def _FromDict(self, data: dict[str, object]) -> None:
        super()._FromDict(data)
        self.__number_requests = data["number_requests"]
        self.__request_limit = data["request_limit"]

    def can_be_used(self) -> bool:
        return self.__number_requests < self.request_limit

    def should_reset(self) -> bool:
        return self.last_access != date.today()

    def reset(self) -> None:
        self.__number_requests = 0
        self.last_access = date.today()

    def __repr__(self) -> str:
        return f"<NTT API: {self.key} - Requests: {self.number_requests} />"
