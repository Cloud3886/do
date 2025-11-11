import json
import random
import string
from typing import Any


def hash_gen(size=6, chars=string.ascii_lowercase):
    return "".join(random.choice(chars) for _ in range(size))


def prettify(data):
    return json.dumps(
        data,
        indent=4,
        separators=(",", ": "),
        default=lambda o: str(o.__class__.__name__),
    )


def asdict(obj) -> dict[str, Any]:
    json = {}
    for key in dir(obj):
        value = getattr(obj, key)
        if not (key.startswith("_") or callable(value)):
            json[key] = getattr(obj, key)
    return json
