#!/usr/bin/env python3
"""Validate the JSON Schema subset used by this book; no external dependency."""
import argparse
import json
from pathlib import Path
import re

KEYWORDS = {"$schema", "title", "description", "type", "properties", "required",
            "additionalProperties", "items", "enum", "minimum", "pattern", "minItems"}


def validate(value, schema, location="$"):
    unsupported = set(schema) - KEYWORDS
    if unsupported:
        raise ValueError(f"Unsupported schema keywords: {sorted(unsupported)}")
    kind = schema.get("type")
    checks = {"object": lambda v: isinstance(v, dict), "array": lambda v: isinstance(v, list),
              "string": lambda v: isinstance(v, str), "integer": lambda v: type(v) is int,
              "boolean": lambda v: type(v) is bool}
    if kind is not None and (kind not in checks or not checks[kind](value)):
        raise ValueError(f"{location}: expected {kind}")
    if "enum" in schema and value not in schema["enum"]:
        raise ValueError(f"{location}: value outside enum")
    if "minimum" in schema and value < schema["minimum"]:
        raise ValueError(f"{location}: below minimum")
    if "pattern" in schema and re.search(schema["pattern"], value) is None:
        raise ValueError(f"{location}: pattern mismatch")
    if isinstance(value, dict):
        for name in schema.get("required", []):
            if name not in value:
                raise ValueError(f"{location}: missing {name}")
        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for name, child in value.items():
            if name in properties:
                validate(child, properties[name], f"{location}.{name}")
            elif additional is False:
                raise ValueError(f"{location}: unexpected {name}")
            elif isinstance(additional, dict):
                validate(child, additional, f"{location}.{name}")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            raise ValueError(f"{location}: too few items")
        for index, child in enumerate(value):
            if "items" in schema:
                validate(child, schema["items"], f"{location}[{index}]")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("schema")
    parser.add_argument("data")
    parser.add_argument("--jsonl", action="store_true")
    args = parser.parse_args()
    schema = json.loads(Path(args.schema).read_text())
    data = Path(args.data).read_text()
    rows = [json.loads(line) for line in data.splitlines() if line.strip()] if args.jsonl else [json.loads(data)]
    for row in rows:
        validate(row, schema)
    print("SCHEMA OK")


if __name__ == "__main__":
    main()
