from datetime import date, timedelta
import json
import os
from parameterized import parameterized
from typing import List
import unittest
from ntt_api_management import *


class APIManagementTest(unittest.TestCase):
    test_data_file = "test_data.json"
    first_api = "first-api"
    second_api = "second-api"
    test_limit = 10
    test_data_minute_limit_mode_file = "test_data_minute_limit_mode.json"

    def setUp(self) -> None:
        self.__CleanDataFile()
        NTTAPIDailyLimit.daily_limit = self.test_limit

        self.apiWith2APIs = NTTAPIManagement(
            data_json_file=self.test_data_file,
        )
        self.apiWith2APIs.add_api(self.first_api)
        self.apiWith2APIs.add_api(self.second_api)

        self.apiWith2APIInMinuteLimitMode = NTTAPIManagement(
            data_json_file=self.test_data_minute_limit_mode_file,
            api_mode=NTTAPIMode.MINUTE_LIMIT,
        )
        self.apiWith2APIInMinuteLimitMode.add_api(self.first_api)
        self.apiWith2APIInMinuteLimitMode.add_api(self.second_api)

    def tearDown(self) -> None:
        self.__CleanDataFile()

    def __CleanDataFile(self) -> None:
        if os.path.exists(self.test_data_file):
            os.remove(self.test_data_file)

        if os.path.exists(self.test_data_minute_limit_mode_file):
            os.remove(self.test_data_minute_limit_mode_file)

    def test_GivenAPIManagement_WhenAskAPI_ThenReturnEmpty(self) -> None:
        api = NTTAPIManagement()

        self.assertIsNone(api.API)

    def test_GivenAPIManagementWithAddedAPI_WhenAskAPI_ThenReturnAPI(self) -> None:
        api = NTTAPIManagement()

        api.add_api(self.first_api)

        self.__APIShouldHasKey(api.API, self.first_api)
        self.__APIsShouldHaveKeys(api.APIs, [self.first_api])

    def __APIShouldHasKey(self, api: INTTAPI, key: str) -> None:
        self.assertEqual(api.key, key)

    def __APIsShouldHaveKeys(self, apis: List[INTTAPI], keys: List[str]) -> None:
        self.assertEqual(len(apis), len(keys))
        for i in range(len(apis)):
            self.__APIShouldHasKey(apis[i], keys[i])

    def test_GivenAPIManagementWithAddedAPI_WhenAddNewAPI_ThenThePreviousAPIIsUsed(
        self,
    ) -> None:
        api = NTTAPIManagement()
        api.add_api(self.first_api)

        api.add_api(self.second_api)

        self.__APIShouldHasKey(api.API, self.first_api)
        self.__APIsShouldHaveKeys(api.APIs, [self.first_api, self.second_api])
        self.assertEqual(api.API.number_requests, 0)

    def test_GivenAPIManagementWithAddedAPI_WhenCreateOtherInstance_ThenTheAPIsAreShared(
        self,
    ) -> None:
        api = NTTAPIManagement(data_json_file=self.test_data_file)
        api.add_api(self.first_api)

        other_api = NTTAPIManagement(data_json_file=self.test_data_file)

        self.__APIShouldHasKey(other_api.API, self.first_api)

    def test_GivenAddedAPI_WhenMakeARequest_ThenTheNumberOfRequestsIsIncreased(
        self,
    ) -> None:
        api = NTTAPIManagement()
        api.add_api(self.first_api)

        api.make_request()

        self.assertEqual(api.API.number_requests, 1)

    def test_GivenNoAPIAdded_WhenMakeARequest_ThenNoError(self) -> None:
        api = NTTAPIManagement()

        api.make_request()

    def test_Given2APIsWhenTheFirstOneReachesTheLimit_ThenTheSecondOneIsUsed(
        self,
    ) -> None:
        limit = 10
        api = NTTAPIManagement()
        first_api = "first-api"
        second_api = "second-api"
        api.add_api(first_api)
        api.add_api(second_api)

        for _ in range(limit):
            api.make_request()

        self.__APIShouldHasKey(api.API, second_api)

    @parameterized.expand(
        [
            (5, 5, 0),
            (10, 10, 0),
            (11, 10, 1),
            (14, 10, 4),
        ]
    )
    def test_Given2APIs_ThenTheirNumberOfRequestsAreSave(
        self,
        make_requests,
        first_api_requests,
        second_api_requests,
    ) -> None:
        for _ in range(make_requests):
            self.apiWith2APIs.make_request()

        other_api = NTTAPIManagement(data_json_file=self.test_data_file)

        self.assertEqual(len(other_api.APIs), len(self.apiWith2APIs.APIs))
        self.assertEqual(other_api.APIs[0].number_requests, first_api_requests)
        self.assertEqual(other_api.APIs[1].number_requests, second_api_requests)
        self.__ItShouldHasTheNumberOfRequestsAsExpected(
            other_api.APIs,
            [
                first_api_requests,
                second_api_requests,
            ],
        )

    def __ItShouldHasTheNumberOfRequestsAsExpected(
        self,
        apis: List[INTTAPI],
        requests: List[int],
    ) -> None:
        for i in range(len(apis)):
            self.assertEqual(apis[i].number_requests, requests[i])

    @parameterized.expand(
        [
            (5, 6, 0),
            (10, 10, 1),
            (11, 10, 2),
            (14, 10, 5),
        ]
    )
    def test_Given2APIs_WhenAnotherAPIMakeRequest_ThenTheNumberOfRequestsAreIncreased(
        self,
        previous_requests,
        first_api_requests,
        second_api_requests,
    ) -> None:
        for _ in range(previous_requests):
            self.apiWith2APIs.make_request()

        other_api = NTTAPIManagement(
            data_json_file=self.test_data_file,
        )

        other_api.make_request()

        self.__ItShouldHasTheNumberOfRequestsAsExpected(
            other_api.APIs,
            [
                first_api_requests,
                second_api_requests,
            ],
        )

    def test_Given2APIs_WhenLoadTheFileWithError_ThenTheFileIsResetToDefaultValidDataFile(
        self,
    ) -> None:
        self.__FakeTheDataFileToInvalidJsonFormat()
        api = NTTAPIManagement(data_json_file=self.test_data_file)

        self.assertIsNone(api.API)
        self.__APIsShouldHaveKeys(api.APIs, [])

    def __FakeTheDataFileToInvalidJsonFormat(self) -> None:
        with open(self.test_data_file, "w") as file:
            file.write('{"date": "2021-10-10"}, "data": [{"key"}')

    def test_Given2APIs_WhenLoadTheFirstTimeInToday_ThenTheNumberOfRequestsAreReset(
        self,
    ) -> None:
        for _ in range(5):
            self.apiWith2APIs.make_request()

        self.__FakeDateToYesterday(self.apiWith2APIs)

        other_api = NTTAPIManagement(data_json_file=self.test_data_file)

        self.__ItShouldHasTheNumberOfRequestsAsExpected(
            other_api.APIs,
            [
                0,
                0,
            ],
        )

    def __FakeDateToYesterday(self, manager: NTTAPIManagement) -> None:
        for api in manager.APIs:
            api.last_access = date.today() - timedelta(days=1)

        manager.UpdateDataFile()

    def test_GivenAPIInEachMinuteMode_WhenMakeRequest_ThenTheAPIIsChanged(self) -> None:
        api = NTTAPIManagement(
            api_mode=NTTAPIMode.MINUTE_LIMIT,
        )

        api.add_api(self.first_api)
        api.add_api(self.second_api)

        api.make_request()

        self.__APIShouldHasKey(api.API, self.second_api)

    def test_GivenAPIInEachMinuteMode_WhenMakeRequestThatTheFirstOneRequestLessThan1Minute_ThenAPICannotBeCalled(
        self,
    ) -> None:
        for _ in range(2):
            self.apiWith2APIInMinuteLimitMode.make_request()

        self.assertIsNone(self.apiWith2APIInMinuteLimitMode.API)

    def test_GivenAPIInEachMinuteMode_WhenCreateTheNewInstance_ThenTheAPIsAreShared(
        self,
    ) -> None:
        self.apiWith2APIInMinuteLimitMode.make_request()

        other_api = NTTAPIManagement(
            data_json_file=self.test_data_minute_limit_mode_file,
            api_mode=NTTAPIMode.MINUTE_LIMIT,
        )

        print(other_api.APIs)
        self.__APIShouldHasKey(other_api.API, self.second_api)

    def test_GivenAPIInEachMinuteModeWithPrevRequestIs2MinutesAgo_WhenAskAPI_ThenItShouldReturn(
        self,
    ) -> None:
        self.apiWith2APIInMinuteLimitMode.make_request()
        self.apiWith2APIInMinuteLimitMode.make_request()
        self.__FakeDateTo2MinutesAgo(self.apiWith2APIInMinuteLimitMode)

        self.__APIShouldHasKey(self.apiWith2APIInMinuteLimitMode.API, self.first_api)

    def __FakeDateTo2MinutesAgo(self, api: NTTAPIManagement) -> None:
        api.APIs[0].last_request_time = api.APIs[0].last_request_time - timedelta(
            minutes=2
        )
