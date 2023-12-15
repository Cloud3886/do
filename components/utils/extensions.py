import json
import random
import string


def hash_gen(size=6, chars=string.ascii_lowercase):
    return "".join(random.choice(chars) for _ in range(size))


def prettify(data):
    return json.dumps(
        data,
        indent=4,
        separators=(",", ": "),
        default=lambda o: str(o.__class__.__name__),
    )
