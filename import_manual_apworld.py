import os
import json
import zipfile
import base64

from os import listdir
from os.path import isfile, join

from utils import abspath, load_progressions, world_folder

input_folder = join(abspath, "input")

def extract_manual(fname):
    archive = zipfile.ZipFile(fname, 'r')
    dirs = list(set([os.path.dirname(x) for x in archive.namelist()]))
    dirs.sort(key=lambda x: len(x))
    if '' in dirs:
        dirs.remove('')
    top_dir = dirs[0].split('/')[0]
    gamedata = json.load(archive.open(f'{top_dir}/data/game.json'))
    itemdata = json.load(archive.open(f'{top_dir}/data/items.json'))

    game_name = f"Manual_{gamedata['game']}_{gamedata.get('creator',gamedata.get('player'))}"
    game_folder = os.path.join(world_folder, game_name)
    os.makedirs(game_folder, exist_ok=True)

    game_file = os.path.join(game_folder, "progression.txt")
    items = load_progressions(game_name)

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

def extract_patch(fname):
    text = open(fname, "r", encoding="utf-8").read()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = json.loads(base64.b64decode(text).decode("utf-8"))
    game_name = data['game']
    items = load_progressions(game_name)
    for name, item in data['items'].items():
        if items.get(name) != "unknown":
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

if os.path.exists(input_folder):
    InputApworlds = [os.path.join(input_folder, f) for f in listdir(input_folder) if isfile(join(input_folder, f)) and f.lower().startswith("manual_")]
    InputApManuals = [os.path.join(input_folder, f) for f in listdir(input_folder) if isfile(join(input_folder, f)) and f.endswith(".apmanual")]
else:
    InputApworlds = []
    InputApManuals = []
try:
    import platformdirs
    custom_worlds = os.path.join(platformdirs.site_data_dir(), "Archipelago", "custom_worlds")
    if os.path.exists(custom_worlds):
        InputApworlds.extend([os.path.join(custom_worlds, f) for f in listdir(custom_worlds) if isfile(join(custom_worlds, f)) and f.lower().startswith("manual_")])
except ImportError:
    print("platformdirs not found, can't scan custom worlds")
    pass

if not InputApworlds:
    print("No manual files found")
    exit(1)

for manual in InputApworlds:
    extract_manual(manual)
for manual in InputApManuals:
    extract_patch(manual)
print("done")
