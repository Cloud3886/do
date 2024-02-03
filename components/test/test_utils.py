from typing import Any, cast

from components.utils.deepset import deepset


def test_deepset():
    data = {
        "one": 11,
        "nested": {"three": 13},
        "listed": ["fourteen"],
        "nlisted": {"twelve": 12, "listed": ["fifteen"]},
        "lnested": [{"dnested": {"final": "end"}}],
    }
    main = {
        "one": 1,
        "two": 2,
        "nested": {"three": 3},
        "listed": ["four"],
        "nlisted": {
            "five": 5,
            "listed": ["six", "seven"],
        },
        "lnested": [
            {"eight": 8},
            {"nine": 9, "ten": 10},
            {"dnested": {"final": "end"}},
        ],
    }

    result = deepset(main, data)

    assert result["one"] == 11
    assert result["two"] == 2
    assert result["nested"]["three"] == 13
    assert "four" in result["listed"]
    assert "fourteen" in result["listed"]
    assert result["nlisted"]["five"] == 5
    assert result["nlisted"]["twelve"] == 12
    assert "six" in result["nlisted"]["listed"]
    assert "seven" in result["nlisted"]["listed"]
    assert "fifteen" in result["nlisted"]["listed"]
    assert {"eight": 8} in result["lnested"]
    assert {"nine": 9, "ten": 10} in result["lnested"]
    assert {"dnested": {"final": "end"}} in result["lnested"]
    assert cast(list, result["lnested"]).count({"dnested": {"final": "end"}}) == 2
