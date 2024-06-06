from datetime import date, timedelta
import json
import os
from parameterized import parameterized
from typing import List
import unittest
from ntt_api_management import *
from .ntt_daily_limit_api import *


class APIManagementDailyLimitTest(unittest.TestCase):
    test_data_file = "test_data.json"
    first_api = "first-api"
    second_api = "second-api"
    test_limit = 10

    def setUp(self) -> None:
        self.__CleanDataFile()
        NTTAPIDailyLimit.daily_limit = self.test_limit

        self.apiWith2APIs = NTTAPIManagement(
            data_json_file=self.test_data_file,
            api_model=NTTAPIDailyLimit,
        )
        self.apiWith2APIs.add_api(self.first_api, request_limit=self.test_limit)
        self.apiWith2APIs.add_api(self.second_api, request_limit=self.test_limit)

    def tearDown(self) -> None:
        self.__CleanDataFile()

    def __CleanDataFile(self) -> None:
        if os.path.exists(self.test_data_file):
            os.remove(self.test_data_file)

    def test_GivenAPIManagement_WhenAskAPI_ThenReturnEmpty(self) -> None:
        api = NTTAPIManagement(NTTAPIDailyLimit)

        self.assertIsNone(api.API)

    def test_GivenAPIManagementWithAddedAPI_WhenAskAPI_ThenReturnAPI(self) -> None:
        api = NTTAPIManagement(NTTAPIDailyLimit)

        api.add_api(self.first_api, request_limit=self.test_limit)

        self.assertEqual(api.API.key, self.first_api)
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
        api = NTTAPIManagement(NTTAPIDailyLimit)
        api.add_api(self.first_api, request_limit=self.test_limit)

        api.add_api(self.second_api, request_limit=self.test_limit)

        self.__APIShouldHasKey(api.API, self.first_api)
        self.__APIsShouldHaveKeys(api.APIs, [self.first_api, self.second_api])
        self.assertEqual(api.API.number_requests, 0)

    def test_GivenAPIManagementWithAddedAPI_WhenCreateOtherInstance_ThenTheAPIsAreShared(
        self,
    ) -> None:
        api = NTTAPIManagement(
            NTTAPIDailyLimit,
            data_json_file=self.test_data_file,
        )
        api.add_api(self.first_api, request_limit=self.test_limit)

        other_api = NTTAPIManagement(
            NTTAPIDailyLimit,
            data_json_file=self.test_data_file,
        )

        self.assertEqual(other_api.API.key, self.first_api)

    def test_GivenAddedAPI_WhenMakeARequest_ThenTheNumberOfRequestsIsIncreased(
        self,
    ) -> None:
        api = NTTAPIManagement(NTTAPIDailyLimit)
        api.add_api(self.first_api, request_limit=self.test_limit)

        api.make_request()

        self.assertEqual(api.API.number_requests, 1)

    def test_GivenNoAPIAdded_WhenMakeARequest_ThenNoError(self) -> None:
        api = NTTAPIManagement(NTTAPIDailyLimit)

        api.make_request()

    def test_Given2APIsWhenTheFirstOneReachesTheLimit_ThenTheSecondOneIsUsed(
        self,
    ) -> None:
        limit = 10
        api = NTTAPIManagement(NTTAPIDailyLimit)
        first_api = "first-api"
        second_api = "second-api"
        api.add_api(first_api, request_limit=limit)
        api.add_api(second_api, request_limit=limit)

        for _ in range(limit):
            api.make_request()

        self.assertEqual(api.API.key, second_api)

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

        other_api = NTTAPIManagement(
            NTTAPIDailyLimit, data_json_file=self.test_data_file
        )

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
            (18, 10, 9),
            (22, 10, 10),
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
            NTTAPIDailyLimit,
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
        api = NTTAPIManagement(NTTAPIDailyLimit, data_json_file=self.test_data_file)

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

        other_api = NTTAPIManagement(
            NTTAPIDailyLimit, data_json_file=self.test_data_file
        )

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
