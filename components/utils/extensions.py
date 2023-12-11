import json
import string
import random

from typing import Callable, TypeVar

T = TypeVar("T")


def replace_element_in_iterable(
    datalist: list[T],
    element: T,
    compare: Callable[[T, T], bool] = lambda x, y: x == y,
) -> bool:
    try:
        matches = [datalist.index(x) for x in datalist if compare(x, element)]
        for match in matches:
            datalist.pop(match)
    except KeyError:
        pass

    datalist.append(element)


def hash_gen(size=6, chars=string.ascii_lowercase):
    return "".join(random.choice(chars) for _ in range(size))


def prettify(data):
    return json.dumps(
        data,
        indent=4,
        separators=(",", ": "),
        default=lambda o: str(o.__class__.__name__),
    )
