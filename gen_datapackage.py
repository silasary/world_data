"""
Hacky little thing to populate progression.txt with all items from a datapackage.
"""
import json
import os
import re
import requests

game = input("Enter game: ")
checksum = None
dp = None
try:
    cache_path = os.path.expandvars(f"%LOCALAPPDATA%/Archipelago/Cache/datapackage/{game}/")
    # I think this cache comes from the .NET client?  If it exists, it's helpful, if not, we'll just fetch the datapackage from the API.
    if os.path.exists(cache_path):
        checksums = [os.path.splitext(f)[0] for f in os.listdir(cache_path)]
        if len(checksums) == 1:
            checksum = checksums[0]
        else:
            print("Multiple checksums found: ")
            for i, c in enumerate(checksums):
                print(f"{i}: {c}")
            checksum = checksums[int(input("Enter index: "))]
    if checksum:
        dp = json.load(open(f"{cache_path}{checksum}.json", "r", encoding="utf-8"))
except Exception as e:
    print(e)

if not checksum:
    checksum = input("Enter checksum:")

if not dp:
    dp = requests.get(f"https://archipelago.gg/api/datapackage/{checksum}").json()
items = {}
for item in dp['item_name_to_id'].keys():
    items[item] = "unknown"

try:
    progressionFile = open(f"worlds/{game}/progression.txt", "r", encoding="utf-8")
    text = progressionFile.read()
    progressionFile.close()
    for x in text.splitlines():
        match = re.match(r"(.*): (.*)", x)
        items[match[1]] = match[2]
except FileNotFoundError:
    pass

with open(f"worlds/{game}/progression.txt", "w", encoding="utf-8") as f:
    for item in items:
        f.write(f"{item}: {items[item]}\n")
