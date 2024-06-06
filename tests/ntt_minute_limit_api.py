from ntt_api_management import *
from datetime import datetime, timedelta


class NTTAPIMinuteLimit(NTTAPIBase):
    def __init__(
        self,
        key: str = "",
        request_times: int = 0,
        last_request_time: datetime = datetime.now(),
    ) -> None:
        super().__init__(key, last_request_time)
        self.__request_times = request_times

    @property
    def number_requests(self) -> int:
        return self.__request_times

    def _make_request(self, **kwargs) -> None:
        super()._make_request(**kwargs)
        self.__request_times += 1

    def can_be_used(self) -> bool:
        if self.__request_times == 0:
            return True
        elif self.last_request_time < datetime.now() - timedelta(minutes=1):
            return True
        else:
            return False

    def ToDict(self) -> dict[str, object]:
        baseDict = super().ToDict()

        baseDict["request_times"] = self.__request_times
        return baseDict

    def _PreprocessIncomingDict(self, data: dict[str, object]) -> None:
        super()._PreprocessIncomingDict(data)

    def _FromDict(self, data: dict[str, object]) -> None:
        super()._FromDict(data)
        self.__request_times = data["request_times"]
