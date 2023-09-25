import orjson
import uuid


def is_valid_uuid(value):
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False


def make_response_message(data):
    return orjson.dumps({'message': data})
