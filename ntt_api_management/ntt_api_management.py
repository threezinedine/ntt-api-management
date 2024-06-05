from datetime import date, datetime, timedelta
import json
import os
from typing import Optional, List
from .ntt_api import NTTAPI
from .ntt_api_mode import NTTAPIMode


class NTTAPIManagement:
    date_key = "date"
    data_key = "data"

    def __init__(
        self,
        limit: int = 300,
        data_json_file: Optional[str] = None,
        api_mode: NTTAPIMode = NTTAPIMode.DAILY_LIMIT,
    ) -> None:
        self.__apis: List[NTTAPI] = []
        self.__current_api_index: int = -1
        self.__data_json_file = data_json_file
        self.__limit = limit
        self.__api_mode = api_mode

        # check data_json_file exists
        if data_json_file is not None and os.path.exists(data_json_file):
            self.__LoadDataFromFile()

    def __LoadDataFromFile(self) -> None:
        if self.__data_json_file is None:
            return

        try:
            with open(self.__data_json_file, "r") as file:
                data = json.loads(file.read())
        except:
            self.__UpdateDataFile()
            return

        day = datetime.strptime(data[self.date_key], "%Y-%m-%d").date()
        self.__apis = [NTTAPI.FromDict(data) for data in data[self.data_key]]

        if day != date.today():
            self.__ResetAPIs()
            self.__UpdateDataFile()

        self.__UpdateAPIIndex()

    def __ResetAPIs(self) -> None:
        for api in self.__apis:
            api.number_requests = 0

    def __UpdateDataFile(self) -> None:
        if self.__data_json_file is None:
            return

        data_dicts = [api.ToDict() for api in self.__apis]

        today = date.today()

        data = {
            self.date_key: str(today),
            self.data_key: data_dicts,
        }

        with open(self.__data_json_file, "w") as file:
            file.write(json.dumps(data))

    @property
    def API(self) -> NTTAPI:
        self.__UpdateAPIIndex()

        if self.__current_api_index < 0:
            return None

        return self.__apis[self.__current_api_index]

    @property
    def APIs(self) -> List[NTTAPI]:
        return self.__apis

    def add_api(self, api_key: str) -> None:
        api = NTTAPI(key=api_key)
        self.__apis.append(api)
        self.__UpdateDataFile()

        if self.__current_api_index < 0:
            self.__current_api_index = 0

    def make_request(self) -> None:
        if self.API is None:
            return

        api = self.API
        api.last_request_time = datetime.now()
        api.number_requests += 1

        self.__UpdateAPIIndex()
        self.__UpdateDataFile()

    def __UpdateAPIIndex(self) -> None:
        if len(self.__apis) == 0:
            pass
        elif self.__api_mode == NTTAPIMode.MINUTE_LIMIT:
            for i in range(len(self.__apis)):
                if self.__apis[i].number_requests == 0:
                    self.__current_api_index = i
                    return
                elif self.__apis[i].last_request_time < datetime.now() - timedelta(
                    minutes=1
                ):
                    self.__current_api_index = i
                    return
        else:
            for i in range(len(self.__apis)):
                if self.__apis[i].number_requests < self.__limit:
                    self.__current_api_index = i
                    return

        self.__current_api_index = -1
