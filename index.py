from config import URL, KEY
from supabase import create_client, Client

supabase: Client = create_client(URL, KEY)


def handler(event, context):
    """
    Entry-point for Serverless Function.
    :param event: request payload.
    :param context: information about current execution context.
    :return: response to be serialized as JSON.
    """
    text = "Hello! I'll repeat anything you say to me."
    if (
        "request" in event
        and "original_utterance" in event["request"]
        and len(event["request"]["original_utterance"]) > 0
    ):
        text = event["request"]["original_utterance"]
    print(test())
    return {
        "version": event["version"],
        "session": event["session"],
        "response": {
            # Respond with the original request or welcome the user if this is the beginning of the dialog and the request has not yet been made.
            "text": "test",
            # Don't finish the session after this response.
            "end_session": "false",
        },
    }


def test():
    import requests as req

    r = req.get("http://2ip.ru")

    return r.text


if __name__ == "__main__":
    test()
