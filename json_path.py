#!/usr/bin/env python3
"""json_path - JSONPath query engine for nested data extraction."""
import sys, re

def query(data, path):
    if path == "$": return [data]
    parts = _parse(path)
    return _resolve(data, parts)

def _parse(path):
    tokens = []
    i = 0
    s = path.lstrip("$")
    for part in re.findall(r'\.\.|\.?\w+|\[\d+\]|\[\*\]|\*', s):
        if part.startswith("[") and part.endswith("]"):
            inner = part[1:-1]
            tokens.append(("index", int(inner)) if inner != "*" else ("wildcard",))
        elif part == "..":
            tokens.append(("recursive",))
        elif part == "*":
            tokens.append(("wildcard",))
        else:
            tokens.append(("key", part.lstrip(".")))
    return tokens

def _resolve(data, parts):
    current = [data]
    for part in parts:
        nxt = []
        for item in current:
            if part[0] == "key":
                if isinstance(item, dict) and part[1] in item:
                    nxt.append(item[part[1]])
            elif part[0] == "index":
                if isinstance(item, list) and -len(item) <= part[1] < len(item):
                    nxt.append(item[part[1]])
            elif part[0] == "wildcard":
                if isinstance(item, dict): nxt.extend(item.values())
                elif isinstance(item, list): nxt.extend(item)
            elif part[0] == "recursive":
                nxt.extend(_deep(item))
        current = nxt
    return current

def _deep(data):
    result = [data]
    if isinstance(data, dict):
        for v in data.values(): result.extend(_deep(v))
    elif isinstance(data, list):
        for v in data: result.extend(_deep(v))
    return result

def test():
    d = {"store": {"books": [{"title": "A", "price": 10}, {"title": "B", "price": 20}], "name": "Shop"}}
    assert query(d, "$.store.name") == ["Shop"]
    assert query(d, "$.store.books[0].title") == ["A"]
    assert query(d, "$.store.books[*].title") == ["A", "B"]
    assert query(d, "$.store.books[1].price") == [20]
    r = query(d, "$..title")
    assert "A" in r and "B" in r
    print("json_path: all tests passed")

if __name__ == "__main__":
    test() if "--test" in sys.argv else print("Usage: json_path.py --test")
