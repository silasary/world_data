import os
import json
import re
import zipfile

from os import listdir
from os.path import isfile, join

abspath = os.path.dirname(__file__)
input_folder = join(abspath, "input")
world_folder = join(abspath, "worlds")

def extract_manual(fname):
    archive = zipfile.ZipFile(fname, 'r')
    dirs = list(set([os.path.dirname(x) for x in archive.namelist()]))
    top_dir = dirs[0].split('/')[0]
    gamedata = json.load(archive.open(f'{top_dir}/data/game.json'))
    itemdata = json.load(archive.open(f'{top_dir}/data/items.json'))

    game_name = f"Manual_{gamedata['game']}_{gamedata.get('creator',gamedata.get('player'))}"
    game_folder = os.path.join(world_folder, game_name)
    os.makedirs(game_folder, exist_ok=True)

    game_file = os.path.join(game_folder, "progression.txt")
    items = {}
    try:
        progressionFile = open(os.path.join(world_folder, game_name, "progression.txt"), "r", encoding="utf-8")
        text = progressionFile.read()
        progressionFile.close()
        for x in text.splitlines():
            match = re.match(r"(.*): (.*)", x)
            items[match[1]] = match[2]
    except FileNotFoundError:
        pass

    with open(game_file, "w+", encoding="utf-8") as f:
        default_filler = gamedata.get('filler_item_name', '')
        if default_filler:
            f.write(f"{gamedata['filler_item_name']}: filler\n")
        for item in itemdata:
            if default_filler and item['name'] == default_filler:
                continue
            classification = "filler"
            if item.get("trap"):
                classification = "trap"
            elif item.get("progression_skip_balancing"):
                classification = "mcguffin"
            elif item.get("progression"):
                classification = "progression"
            elif item.get("useful"):
                classification = "useful"
            items[item['name']] = classification

    with open(os.path.join(world_folder, game_name, "progression.txt"), "w", encoding="utf-8") as f:
        for item in items:
            f.write(f"{item}: {items[item]}\n")

    archive.close()

if os.path.exists(input_folder):
    InputApworlds = [f for f in listdir(input_folder) if isfile(join(input_folder, f)) and f.lower().startswith("manual_")]
else:
    InputApworlds = []
try:
    import platformdirs
    custom_worlds = os.path.join(platformdirs.site_data_dir(), "Archipelago", "custom_worlds")
    if os.path.exists(custom_worlds):
        InputApworlds.extend([f for f in listdir(custom_worlds) if isfile(join(custom_worlds, f)) and f.lower().startswith("manual_")])
        input_folder = custom_worlds
except ImportError:
    print("platformdirs not found, can't scan custom worlds")
    pass

if not InputApworlds:
    print("No manual files found")
    exit(1)

for manual in InputApworlds:
    fname = os.path.join(input_folder, manual)
    extract_manual(fname)
print("done")
