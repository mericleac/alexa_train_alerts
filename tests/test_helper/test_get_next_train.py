import datetime
import json

import pytest
from mock import Mock, patch

with open("tests/test_json/test_cta_api.json") as json_file:
    cta_json = json.load(json_file)


@patch("train_alerts.lambda_function.get_stop_id")
@patch("train_alerts.lambda_function.requests")
def test_get_next_train_with_parameters(requests_mock, get_stop_id_mock):
    from train_alerts.lambda_function import get_next_train

    color = "Orange"
    destination = "Loop"
    station = "Pulaski"

    requests_mock.get.return_value = Mock(json=lambda: cta_json)
    get_stop_id_mock.return_value = "mapid=40960"

    res = get_next_train(station=station, color=color, destination=destination)

    assert res == {
        "color": color,
        "destination": destination,
        "station": station,
        "minutes_to_arrival": 2,
    }
    requests_mock.get.assert_called_once()
    get_stop_id_mock.assert_called_once()
