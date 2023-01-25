from urllib import request

from django.core.management import call_command
from django.test import TestCase
from rest_framework.reverse import reverse

from organizations.management.commands.utils import (
    create_a_preconfig,
    create_suported_characteristics,
)
from organizations.models import Product, Repository
from utils.tests import APITestCaseExpanded


class GoalEndpointsTestCase(APITestCaseExpanded):
    def setUp(self):
        characteristics = [
            {
                "key": "functional_suitability",
                "name": "",
                "subcharacteristics": [
                    {"key": "testing_status"},
                ],
            },
            {
                "key": "performance_efficiency",
                "name": "",
                "subcharacteristics": [
                    {"key": "testing_status"},
                ],
            },
            {
                "key": "security",
                "name": "",
                "subcharacteristics": [
                    {"key": "testing_status"},
                ],
            },
        ]
        create_suported_characteristics(characteristics)
        characteristics_keys = [item["key"] for item in characteristics]

        self.org = self.get_organization()
        self.product = self.get_product(self.org)

        create_a_preconfig(
            characteristics_keys=characteristics_keys,
            product=self.product,
        )

    def validate_goal_request(
        self,
        request_data,
        expected_status_code,
        expected_data=None,
    ):
        url = reverse(
            'create-goal-list',
            args=[self.org.id, self.product.id],
        )

        response = self.client.post(url, request_data, format="json")

        self.assertEqual(response.status_code, expected_status_code)

        if response.status_code == 201:
            response_data = response.json()['data']

            if expected_data:
                self.assertEqual(
                    response_data,
                    expected_data,
                    'Equalizer returned a different value than expected',
                )

    def test_if_create_goal_reject_invalid_jsons(self):
        request_data = {
            "release_name": "v1.0.0",
            "created_by": "username",
            "start_at": "2022-08-19",
            "end_at": "2022-09-19",
            "changes": [
                {
                    "characteristic_key": "non existent characteristic",
                    "delta": 10
                },
            ]
        }
        self.validate_goal_request(request_data, expected_status_code=400)

    def tests_if_a_valid_request_with_no_changes_sets_all_weights_to_50(self):
        request_data = {
            "release_name": "v1.0.0",
            "created_by": "username",
            "start_at": "2022-08-19",
            "end_at": "2022-09-19",
            "changes": []
        }

        expected_data = {
            "functional_suitability": 50,
            "performance_efficiency": 50,
            "security": 50,
        }

        self.validate_goal_request(request_data, 201, expected_data)

    def tests_if_a_valid_request_is_returned_values_according_to_the_correlation_matrix(self):
        request_data = {
            "release_name": "v1.0.0",
            "created_by": "username",
            "start_at": "2022-08-19",
            "end_at": "2022-09-19",
            "changes": [
                {
                    "characteristic_key": "functional_suitability",
                    "delta": 10
                },
                {
                    "characteristic_key": "performance_efficiency",
                    "delta": -10
                },
                {
                    "characteristic_key": "security",
                    "delta": 40
                }
            ]
        }

        expected_data = {
            "functional_suitability": 70,
            "performance_efficiency": 0,
            "security": 90,
        }

        self.validate_goal_request(request_data, 201, expected_data)

    def tests_if_a_request_without_the_changes_key_is_refused(self):
        request_data = {
            "release_name": "v1.0.0",
            "created_by": "username",
            "start_at": "2022-08-19",
            "end_at": "2022-09-19",
        }

        expected_status_code = 400

        self.validate_goal_request(request_data, expected_status_code)

    def tests_if_multiple_changes_to_the_same_entity_are_supported(self):
        request_data = {
            "release_name": "v1.0.0",
            "created_by": "username",
            "start_at": "2022-08-19",
            "end_at": "2022-09-19",
            "changes": [
                {
                    "characteristic_key": "functional_suitability",
                    "delta": 10
                },
                {
                    "characteristic_key": "functional_suitability",
                    "delta": 10
                },
                {
                    "characteristic_key": "functional_suitability",
                    "delta": 10
                },
                {
                    "characteristic_key": "functional_suitability",
                    "delta": 10
                },
                {
                    "characteristic_key": "functional_suitability",
                    "delta": 10
                },
            ]
        }

        expected_data = {
            "functional_suitability": 100,
            "performance_efficiency": 0,
            "security": 0,
        }

        self.validate_goal_request(request_data, 201, expected_data)

    def tests_if_undoing_the_change_in_the_entity_goes_back_to_the_previous_weights(self):
        request_data = {
            "release_name": "v1.0.0",
            "created_by": "username",
            "start_at": "2022-08-19",
            "end_at": "2022-09-19",
            "changes": [
                {
                    "characteristic_key": "functional_suitability",
                    "delta": 10
                },
                {
                    "characteristic_key": "functional_suitability",
                    "delta": -10
                },
            ]
        }

        expected_data = {
            "functional_suitability": 50,
            "performance_efficiency": 50,
            "security": 50,
        }

        self.validate_goal_request(request_data, 201, expected_data)

    def tests_whether_100_is_always_the_highest_possible_value_of_a_weight(self):
        request_data = {
            "release_name": "v1.0.0",
            "created_by": "username",
            "start_at": "2022-08-19",
            "end_at": "2022-09-19",
            "changes": [
                {
                    "characteristic_key": "functional_suitability",
                    "delta": 90
                },
                {
                    "characteristic_key": "functional_suitability",
                    "delta": 90
                },
            ]
        }

        expected_data = {
            "functional_suitability": 100,
            "performance_efficiency": 0,
            "security": 0,
        }

        self.validate_goal_request(request_data, 201, expected_data)

    def test_if_two_consecutives_requests_the_second_failure(self):
        request_data = {
            "release_name": "v1.0.0",
            "created_by": "username",
            "start_at": "2022-08-19",
            "end_at": "2022-09-19",
            "changes": [
                {
                    "characteristic_key": "functional_suitability",
                    "delta": 10
                },
                {
                    "characteristic_key": "functional_suitability",
                    "delta": 10
                },
            ]
        }

        expected_data = {
            "functional_suitability": 70,
            "performance_efficiency": 30,
            "security": 30,
        }

        self.validate_goal_request(request_data, 201, expected_data)
        self.validate_goal_request(request_data, 400, expected_data)
