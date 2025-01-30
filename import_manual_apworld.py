import os
import json
import zipfile

from os import listdir
from os.path import isfile, join

abspath = os.path.dirname(__file__)
input_folder = abspath+ "\\input"
world_folder = abspath+ "\\worlds"

InputApworlds = [f for f in listdir(input_folder) if isfile(join(input_folder, f)) and f.lower().startswith("manual_")]

for manual in InputApworlds:
    fname = os.path.join(input_folder, manual)
    archive = zipfile.ZipFile(fname, 'r')
    dirs = list(set([os.path.dirname(x) for x in archive.namelist()]))
    top_dir = dirs[0].split('/')[0]
    gamedata = json.load(archive.open(f'{top_dir}/data/game.json'))
    items = json.load(archive.open(f'{top_dir}/data/items.json'))

    game_name = f"Manual_{gamedata['game']}_{gamedata.get('creator',gamedata.get('player'))}"
    game_folder = os.path.join(world_folder, game_name)
    if not os.path.exists(game_folder):
        os.makedirs(game_folder)

    game_file = os.path.join(game_folder, "progression.txt")

    with open(game_file, "w+", encoding="utf-8") as f:
        default_filler = gamedata.get('filler_item_name', '')
        if default_filler:
            f.write(f"{gamedata['filler_item_name']}: filler\n")
        for item in items:
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
            f.write(f"{item['name']}: {classification}\n")
    archive.close()
print("wow")