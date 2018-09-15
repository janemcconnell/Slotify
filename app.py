# -*- coding: utf-8 -*-
"""
A routing layer for the Slack Spotify Integration built using
[Slack's Events API](https://api.slack.com/events-api) in Python
"""
import json
import bot
from flask import Flask, request, make_response, render_template

pyBot = bot.Bot()
slack = pyBot.client

app = Flask(__name__)


def _event_handler(event_type, slack_event):
    """
    A helper function that routes events from Slack to our Spotify bot
    by event type and subtype.

    Parameters
    ----------
    event_type : str
        type of event recieved from Slack
    slack_event : dict
        JSON response from a Slack reaction event

    Returns
    ----------
    obj
        Response object with 200 - ok or 500 - No Event Handler error

    """
    team_id = slack_event["team_id"]
    # ================ Link Shared Events =============== #
    # When a link is posted, the type of event will be link_shared
    if event_type == "link_shared":
        print("link shared!");
        # # TODO lookup link on Spotify
        # pyBot.onboarding_message(team_id, user_id)
        # return make_response("Welcome Message Sent", 200,)

    # ================ Message Posted Events =============== #
    # When a message was posted in a direct message, the event type will be
    # message. We'll also need to check that this is a message that has been
    # shared by looking into the attachments for "is_shared".
    elif event_type == "message" 
        print("link shared!");
        # # TODO lookup link on Spotify
        # if slack_event["event"]["attachments"][0].get("is_share"):
        #     # Update the onboarding message and check off "Share this Message"
        #     pyBot.update_share(team_id, user_id)
        #     return make_response("Welcome message updates with shared message",
        #                          200,)

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})

# TODO do I need to Auth here? Or is this just bot stuff?
# @app.route("/install", methods=["GET"])
# def pre_install():
#     """This route renders the installation page with 'Add to Slack' button."""
#     # Since we've set the client ID and scope on our Bot object, we can change
#     # them more easily while we're developing our app.
#     client_id = pyBot.oauth["client_id"]
#     scope = pyBot.oauth["scope"]
#     # Our template is using the Jinja templating language to dynamically pass
#     # our client id and scope
#     return render_template("install.html", client_id=client_id, scope=scope)


@app.route("/listening", methods=["GET", "POST"])
def hears():
    """
    This route listens for incoming events from Slack and uses the event
    handler helper function to route events to our Bot.
    """
    slack_event = json.loads(request.data)

    # ============= Slack URL Verification ============ #
    # In order to verify the url of our endpoint, Slack will send a challenge
    # token in a request and check for this token in the response our endpoint
    # sends back.
    #       For more info: https://api.slack.com/events/url_verification
    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                             "application/json"
                                                             })

    # ============ Slack Token Verification =========== #
    # We can verify the request is coming from Slack by checking that the
    # verification token in the request matches our app's settings
    if pyBot.verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s \npyBot has: \
                   %s\n\n" % (slack_event["token"], pyBot.verification)
        # By adding "X-Slack-No-Retry" : 1 to our response headers, we turn off
        # Slack's automatic retries during development.
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    # ====== Process Incoming Events from Slack ======= #
    # If the incoming request is an Event we've subcribed to
    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        # Then handle the event by event_type and have your bot respond
        return _event_handler(event_type, slack_event)
    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


if __name__ == '__main__':
    app.run(debug=True)