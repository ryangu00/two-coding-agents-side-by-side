#!/usr/bin/env python3
"""Protocol placeholder only: consume JSON and return an empty hook response."""
import json
import sys

json.load(sys.stdin)
print("{}")
