"""
Hacky little thing to populate progression.txt with all items from a datapackage.
"""
import json
import os
import re
import requests
import pathlib
import datetime

from utils import world_folder

game = input("Enter game: ")
if not game:
    games = [f for f in os.listdir(os.path.expandvars(f"%LOCALAPPDATA%/Archipelago/Cache/datapackage/"))]
    for i, g in enumerate(games):
        print(f"{i}: {g}")
    game = games[int(input("Enter index: "))]

checksum = None
dp = None
try:
    cache_path = pathlib.Path(os.path.expandvars(f"%LOCALAPPDATA%/Archipelago/Cache/datapackage/{game}/"))
    # CommonClient stores its checksums here, so if you've ever connected to a multiworld with the same game, it should be here
    if cache_path.exists():
        checksums = [f for f in cache_path.iterdir() if f.is_file()]
        if len(checksums) == 1:
            checksum = checksums[0].stem
        else:
            print("Multiple checksums found: ")
            for i, c in enumerate(checksums):
                date = datetime.datetime.fromtimestamp(c.stat().st_mtime)
                print(f"{i}: {c.stem} ({date})")
            checksum = checksums[int(input("Enter index: "))].stem
    if checksum:
        dp = json.load(open(f"{cache_path}/{checksum}.json", "r", encoding="utf-8"))
except Exception as e:
    print(e)

if not checksum:
    checksum = input("Enter checksum:")

if not dp:
    dp = requests.get(f"https://archipelago.gg/api/datapackage/{checksum}").json()
items = {}
for item in dp['item_name_to_id'].keys():
    items[item] = "unknown"

os.makedirs(world_folder / game, exist_ok=True)
try:
    progressionFile = open(world_folder / game / "progression.txt", "r", encoding="utf-8")
    text = progressionFile.read()
    progressionFile.close()
    for x in text.splitlines():
        match = re.match(r"(.*): (.*)", x)
        items[match[1]] = match[2]
except FileNotFoundError:
    pass

with open(world_folder / game / "progression.txt", "w", encoding="utf-8") as f:
    for item in items:
        f.write(f"{item}: {items[item]}\n")
