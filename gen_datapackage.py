"""
Hacky little thing to populate progression.txt with all items from a datapackage.
"""
import json
import os
import re
import requests
import pathlib

try:
    import platformdirs
    datapackage_dir = os.path.join(platformdirs.user_data_dir("Archipelago", False), "Cache", "datapackage")
except ImportError:
    datapackage_dir = os.path.expandvars("%LOCALAPPDATA%/Archipelago/Cache/datapackage")
    pass


from utils import world_folder

def fill_progression_data(game: str, dp: dict):
    items = {}
    if dp:
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
            if match:
                items[match[1]] = match[2]
            else:
                print(f"Failed to parse line: {x}")
    except FileNotFoundError:
        pass

    with open(world_folder / game / "progression.txt", "w", encoding="utf-8") as f:
        for item in items:
            f.write(f"{item}: {items[item]}\n")

def load_game_data_package(game):
    checksum = None
    dp = None
    try:
        cache_path = pathlib.Path(os.path.join(datapackage_dir, game))
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

    if checksum and not dp:
        dp = requests.get(f"https://archipelago.gg/api/datapackage/{checksum}").json()

    fill_progression_data(game, dp)

game = input("Enter game (or enter for list): ")
if game:
    load_game_data_package(game)
else:
    games = [f for f in os.listdir(datapackage_dir)]
    for i, g in enumerate(games):
        print(f"{i}: {g}")
    index = input("Enter index (or enter for everything): ")
    if index:
        game = games[int(index)]
        load_game_data_package(game)
    else:
        for g in games:
            load_game_data_package(g)

