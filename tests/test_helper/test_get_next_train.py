import datetime
import json

import pytest
from mock import Mock, patch
from freezegun import freeze_time

with open("tests/test_json/test_cta_api.json") as json_file:
    cta_json = json.load(json_file)


@freeze_time("2015-04-30 20:20:32")
@patch("train_alerts.lambda_function.requests")
def test_get_next_train_with_parameters(requests_mock):
    from train_alerts.lambda_function import get_next_train

    color = "Orange"
    destination = "Loop"
    station = "Pulaski"

    requests_mock.get.return_value = Mock(json=lambda: cta_json)

    res = get_next_train(color, destination, station)

    assert res == {
        "color": color,
        "destination": destination,
        "station": station,
        "minutes_to_arrival": 5,
    }
    requests_mock.get.assert_called_once()
