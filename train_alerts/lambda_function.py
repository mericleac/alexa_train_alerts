"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import datetime
import math
import json
import requests

route_colors = {
    "Red": "Red",
    "Blue": "Blue",
    "Brn": "Brown",
    "G": "Green",
    "Org": "Orange",
    "P": "Purple",
    "Pink": "Pink",
    "Y": "Yellow",
}

# Will eventually need to add support for purple express
chi_data_color_mapping = {
    "Red": "red",
    "Blue": "blue",
    "Brown": "brn",
    "Green": "g",
    "Orange": "o",
    "Purple": "p",
    "Pink": "pnk",
    "Yellow": "y"
}

direction_mapping = {
    "North": "N",
    "South": "S",
    "East": "E",
    "West": "W"
}

# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {"type": "PlainText", "text": output},
        "card": {
            "type": "Simple",
            "title": "SessionSpeechlet - " + title,
            "content": "SessionSpeechlet - " + output,
        },
        "reprompt": {"outputSpeech": {"type": "PlainText", "text": reprompt_text}},
        "shouldEndSession": should_end_session,
    }


def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response,
    }


# --------------- Helpers that fetch CTA Api data ------------------------------


def get_next_train(station, color=None, destination=None):

    data = requests.get(
        "http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx?key=0fc2e48c0ad84d99923e89e8607776cd&max=1&{query}&outputType=JSON"
        .format(query=get_stop_id(station))
    ).json()

    time_to_arrival = (
        datetime.datetime.strptime(
            data["ctatt"]["eta"][0]["arrT"], "%Y-%m-%dT%H:%M:%S")
        - datetime.datetime.now()
    )

    return {
        "color": route_colors[data["ctatt"]["eta"][0]["rt"]],
        "destination": data["ctatt"]["eta"][0]["destNm"],
        "station": data["ctatt"]["eta"][0]["staNm"],
        "minutes_to_arrival": math.ceil(time_to_arrival.total_seconds() / 60),
    }


def get_stop_id(station, direction=None, destination=None, color=None):
    query = "station_name={station}".format(station=station)
    if direction is not None:
        query += "direction_id={direction}".format(
            direction=direction_mapping[direction])
    if destination is not None:
        query += "$where=stop_name like '%25{destination}%25'".format(
            destination=destination)
    if color is not None:
        query += "{color}=true".format(color=chi_data_color_mapping[color])

    data = requests.get(
        "https://data.cityofchicago.org/resource/8mj8-j3c4.json?{query}"
        .format(query=query)
    ).json()

    return "stpid={stpid}".format(stpid=data[0]["stop_id"]) if len(data) == 1 else "mapid={mapid}".format(mapid=data[0]["map_id"])


# --------------- Functions that control the skill's behavior ------------------


def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = (
        "Thanks for using CTA Train Alerts! "
        "To get started, try asking Alexa: "
        "'When is the next Loop bound Purple "
        "line arriving at Howard?'"
    )
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = (
        "Try asking, "
        "'When is the next Loop bound Purple "
        "line arriving at Howard?'"
    )
    should_end_session = False
    return build_response(
        session_attributes,
        build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session
        ),
    )


def hello_world(intent, session):
    """ Returns a simple hello world message """

    card_title = intent["name"]
    should_end_session = False

    speech_output = "Hello World!"
    reprompt_text = (
        "Hello world is the typical title " "for a developer's first application."
    )
    return build_response(
        {},
        build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session
        ),
    )


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = (
        "Thank you for trying the CTA train alerts skill. " "Have a nice day! "
    )
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response(
        {},
        build_speechlet_response(
            card_title, speech_output, None, should_end_session),
    )


def get_next_train_intent(intent, session):
    card_title = intent["name"]
    should_end_session = True

    color = None
    destination = None

    if intent["slots"].get("station"):
        station = intent["slots"]["station"]["value"]
    else:
        return build_response(
            {},
            build_speechlet_response(
                card_title,
                "Please specify a station in your request",
                None,
                should_end_session
            )
        )
    if intent["slots"].get("color"):
        color = intent["slots"]["color"]["value"]
    if intent["slots"].get("destination"):
        destination = intent["slots"]["station"]["value"]

    data = get_next_train(station, color, destination)

    speech_output = (
        "The next %s bound %s Line train "
        "will be arriving at %s in %s minutes."
        % (
            data["destination"],
            data["color"],
            data["station"],
            data["minutes_to_arrival"],
        )
    )

    return build_response(
        {},
        build_speechlet_response(
            card_title, speech_output, None, should_end_session
        ),
    )


# --------------- Events ------------------


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print(
        "on_session_started requestId="
        + session_started_request["requestId"]
        + ", sessionId="
        + session["sessionId"]
    )


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print(
        "on_launch requestId="
        + launch_request["requestId"]
        + ", sessionId="
        + session["sessionId"]
    )
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print(
        "on_intent requestId="
        + intent_request["requestId"]
        + ", sessionId="
        + session["sessionId"]
    )

    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    # Dispatch to your skill's intent handlers
    if intent_name == "HelloWorldIntent":
        return hello_world(intent, session)
    elif intent_name == "GetNextTrain":
        return get_next_train_intent(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print(
        "on_session_ended requestId="
        + session_ended_request["requestId"]
        + ", sessionId="
        + session["sessionId"]
    )
    # add cleanup logic here


# --------------- Main handler ------------------


def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print(
        "event.session.application.applicationId="
        + event["session"]["application"]["applicationId"]
    )

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event["session"]["new"]:
        on_session_started(
            {"requestId": event["request"]["requestId"]}, event["session"]
        )

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])
