from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError



def report(token, channel, message):
    client = WebClient(token=token)
    try:
        response = client.chat_postMessage(channel=channel, text=message)
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")
