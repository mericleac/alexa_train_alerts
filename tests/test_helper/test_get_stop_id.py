import json

import pytest
from mock import Mock, patch

with open("tests/test_json/test_chi_data_station.json") as json_file:
    station_json = json.load(json_file)

with open("tests/test_json/test_chi_data_station_direction.json") as json_file:
    station_direction_json = json.load(json_file)


@patch("train_alerts.lambda_function.requests")
def test_get_stop_id_with_station(requests_mock):
    from train_alerts.lambda_function import get_stop_id

    station = "Howard"

    requests_mock.get.return_value = Mock(json=lambda: station_json)

    res = get_stop_id(station=station)

    requests_mock.get.assert_called_once()
    assert res == "mapid=40900"


@patch("train_alerts.lambda_function.requests")
def test_get_stop_id_with_station_and_direction(requests_mock):
    from train_alerts.lambda_function import get_stop_id

    station = "Howard"
    direction = "North"

    requests_mock.get.return_value = Mock(json=lambda: station_direction_json)

    res = get_stop_id(station=station, direction=direction)

    requests_mock.get.assert_called_once()
    assert res == "stpid=30175"


@patch("train_alerts.lambda_function.requests")
def test_get_stop_id_with_station_and_destination(requests_mock):
    from train_alerts.lambda_function import get_stop_id

    station = "Howard"
    destination = "Linden"

    requests_mock.get.return_value = Mock(json=lambda: station_direction_json)

    res = get_stop_id(station=station, destination=destination)

    requests_mock.get.assert_called_once()
    assert res == "stpid=30175"
