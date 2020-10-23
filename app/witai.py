from wit import Wit
import os

access_token = os.environ.get("WIT_ACCESS_TOKEN")

client = Wit(access_token)


def response(message_txt):
    resp = client.message(message_txt)
    entity = None
    value = None

    try:
        entity = list(resp["entities"])[0]
        value = resp["entities"][entity]["value"]
    except:
        pass
    return (entity, value)


print(response("How long will my order take"))
