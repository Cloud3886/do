from typing import Any, TypeVar

Data = dict[str, Any] | list[Any]

T = TypeVar("T", dict[str, Any], list[Any])


def deepset(main: T, data: dict[str, Any] | list[Any]) -> T:
    if isinstance(main, list):
        if isinstance(data, list):
            main.extend(data)
        else:
            main.append(data)

    if isinstance(main, dict) and isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                main.setdefault(key, {})
                main[key] = deepset(main[key], value)
            elif isinstance(value, list):
                main.setdefault(key, [])
                main[key].extend(value)
            else:
                main[key] = value

    return main
