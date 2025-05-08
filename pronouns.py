import json
import sys

try:
    with open("pronouns.json") as f:
        pronouns = json.load(f)
        all_pronouns = [x for y in pronouns.values() for x in y]
except FileNotFoundError:
    print("Could not find pronouns.json")
    sys.exit(1)
