import os
import json
from jsonschema import validate

with open("tests/test_json/response_schema.json") as json_file:
    json_schema = json.load(json_file)


def test_request_response_json():
    from train_alerts.lambda_function import lambda_handler

    for filename in os.listdir("tests/test_json/requests"):
        request_json = json.load(open("tests/test_json/requests/" + filename))
        res = lambda_handler(request_json, request_json["context"])

        validate(res, json_schema)
