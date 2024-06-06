import os
import unittest
from ntt_api_management import *
from .ntt_minute_limit_api import *


class APIManagementMinuteLimitTest(unittest.TestCase):
    test_data_file = "test_minute_limit_data.json"
    first_api = "first-api"
    second_api = "second"

    def setUp(self) -> None:
        self.__CleanDataFile()

        self.apiWith2APIs = NTTAPIManagement(
            data_json_file=self.test_data_file,
            api_model=NTTAPIMinuteLimit,
        )
        self.apiWith2APIs.add_api(self.first_api)
        self.apiWith2APIs.add_api(self.second_api)

    def tearDown(self) -> None:
        self.__CleanDataFile()

    def __CleanDataFile(self) -> None:
        if os.path.exists(self.test_data_file):
            os.remove(self.test_data_file)

    def test_GivenAPIs_WhenMakeRequest_ThenTheAPIIsChanged(self) -> None:
        api = NTTAPIManagement(api_model=NTTAPIMinuteLimit)

        api.add_api(self.first_api)
        api.add_api(self.second_api)

        api.make_request()

        self.assertEqual(api.API.key, self.second_api)

    def test_GivenAPI_WhenMakeRequestThatTheFirstOneRequestLessThan1Minute_ThenAPICannotBeCalled(
        self,
    ) -> None:
        for _ in range(2):
            self.apiWith2APIs.make_request()

        self.assertIsNone(self.apiWith2APIs.API)

    def test_GivenAPI_WhenCreateTheNewInstance_ThenTheAPIsAreShared(
        self,
    ) -> None:
        self.apiWith2APIs.make_request()

        other_api = NTTAPIManagement(
            NTTAPIMinuteLimit,
            data_json_file=self.test_data_file,
        )

        self.assertEqual(other_api.API.key, self.second_api)

    def test_GivenAPIWithPrevRequestIs2MinutesAgo_WhenAskAPI_ThenItShouldReturn(
        self,
    ) -> None:
        self.apiWith2APIs.make_request()
        self.apiWith2APIs.make_request()
        self.__FakeDateTo2MinutesAgo(self.apiWith2APIs)

        self.assertEqual(self.apiWith2APIs.API.key, self.first_api)

    def __FakeDateTo2MinutesAgo(self, api: NTTAPIManagement) -> None:
        api.APIs[0].last_request_time = api.APIs[0].last_request_time - timedelta(
            minutes=2
        )
