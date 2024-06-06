from datetime import date, datetime, timedelta
import json
import os
from typing import Optional, List
from .i_ntt_api import INTTAPI


class NTTAPIManagement:
    date_key = "date"
    data_key = "data"

    def __init__(
        self,
        api_model: INTTAPI,
        data_json_file: Optional[str] = None,
    ) -> None:
        self.__apis: List[INTTAPI] = []
        self.__current_api_index: int = -1
        self.__data_json_file = data_json_file
        self.__api_model = api_model

        # check data_json_file exists
        if data_json_file is not None and os.path.exists(data_json_file):
            self.__LoadDataFromFile()

    def __LoadDataFromFile(self) -> None:
        if self.__data_json_file is None:
            return

        try:
            with open(self.__data_json_file, "r") as file:
                data_dicts = json.loads(file.read())
        except:
            self.UpdateDataFile()
            return

        self.__apis = [self.__api_model().FromDict(data) for data in data_dicts]

        self.__CheckResetAPIs()
        self.__UpdateAPIIndex()

    def __CheckResetAPIs(self) -> None:
        for api in self.__apis:
            if api.should_reset():
                api.reset()

        self.UpdateDataFile()

    def UpdateDataFile(self) -> None:
        if self.__data_json_file is None:
            return

        data_dicts = [api.ToDict() for api in self.__apis]

        with open(self.__data_json_file, "w") as file:
            file.write(json.dumps(data_dicts))

    @property
    def API(self) -> INTTAPI:
        self.__UpdateAPIIndex()

        if self.__current_api_index < 0:
            return None

        return self.__apis[self.__current_api_index]

    @property
    def APIs(self) -> List[INTTAPI]:
        return self.__apis

    def add_api(self, api_key: str, **kwargs) -> None:
        self.__apis.append(self.__api_model(key=api_key, **kwargs))

        self.UpdateDataFile()
        self.__UpdateAPIIndex()

    def make_request(self) -> None:
        if self.API is None:
            return

        self.API.make_request()

        self.__UpdateAPIIndex()
        self.UpdateDataFile()

    def __UpdateAPIIndex(self) -> None:
        if len(self.__apis) == 0:
            pass
        else:
            for i in range(len(self.__apis)):
                if self.__apis[i].can_be_used():
                    self.__current_api_index = i
                    return

        self.__current_api_index = -1
