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

def fill_progression_data(game: str, dp: dict):
    items = {}
    for item in dp['item_name_to_id'].keys():
        items[item] = "unknown"

    os.makedirs(world_folder / game, exist_ok=True)
    try:
        progressionFile = open(world_folder / game / "progression.txt", "r", encoding="utf-8")
        text = progressionFile.read()
        progressionFile.close()
        for x in text.splitlines():
            if not x:
                continue
            match = re.match(r"(.*): (.*)", x)
            items[match[1]] = match[2]
    except FileNotFoundError:
        pass

    with open(world_folder / game / "progression.txt", "w", encoding="utf-8") as f:
        for item in items:
            f.write(f"{item}: {items[item]}\n")

def load_game_data_package(game):
    checksum = None
    dp = None
    try:
        cache_path = pathlib.Path(os.path.expandvars(f"%LOCALAPPDATA%/Archipelago/Cache/datapackage/{game}/"))
    # CommonClient stores its checksums here, so if you've ever connected to a multiworld with the same game, it should be here
        if cache_path.exists():
            checksums = [f for f in cache_path.iterdir() if f.is_file()]
            if len(checksums) == 1:
                checksum = checksums[0].stem
                dp = json.load(open(f"{cache_path}/{checksum}.json", "r", encoding="utf-8"))
                fill_progression_data(game, dp)
            else:
                checksums.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                for i, c in enumerate(checksums):
                    checksum = c.stem
                    dp = json.load(open(f"{cache_path}/{checksum}.json", "r", encoding="utf-8"))
                    fill_progression_data(game, dp)
                    return
            return
    except Exception as e:
        print(e)

    if not checksum:
        checksum = input("Enter checksum:")

    if not dp:
        dp = requests.get(f"https://archipelago.gg/api/datapackage/{checksum}").json()

    fill_progression_data(game, dp)

game = input("Enter game: ")
if game:
    load_game_data_package(game)
else:
    games = [f for f in os.listdir(os.path.expandvars(f"%LOCALAPPDATA%/Archipelago/Cache/datapackage/"))]
    for i, g in enumerate(games):
        print(f"{i}: {g}")
    index = input("Enter index: ")
    if index:
        game = games[int(index)]
        load_game_data_package(game)
    else:
        for g in games:
            load_game_data_package(g)

