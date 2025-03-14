import os
from pathlib import Path

from models import ItemClassification, load_datapackage, save_datapackage
from utils import world_folder

valid_classifications = set(ItemClassification.__members__.keys())

unknowns_by_world = {}
all_items = {}

def validate_world(world_name) -> None:
    world_path: Path = world_folder / world_name
    progression_txt = world_path / "progression.txt"
    # if not progression_txt.exists():
    #     raise FileNotFoundError(f"progression.txt not found in {world_name}")
    redirect = world_path / "redirect.txt"
    if redirect.exists() and progression_txt.exists():
        dp = load_datapackage(world_name, None, False)
        dp = load_datapackage(world_name, dp)
        save_datapackage(world_name, dp)
        progression_txt.unlink()
    else:
        dp = load_datapackage(world_name)

    # assert dp.items, f"datapackage for {world_name} is empty"
    unknowns = {i for i in dp.items if dp.items[i] == ItemClassification.unknown}
    if unknowns:
        unknowns_by_world[world_name] = len(unknowns)
    all_items[world_name] = len(dp.items)

for world in os.listdir(world_folder):
    validate_world(world)

unknowns_by_count = sorted(unknowns_by_world.items(), key=lambda x: x[1], reverse=True)
for world, count in unknowns_by_count:
    print(f"{world}: {count} unknowns")

print('\n')
print(f"Total unknowns: {sum(unknowns_by_world.values())}")
print(f"Total worlds with unknowns: {len(unknowns_by_world)}")
print(f"Total worlds: {len(all_items)}")
print(f"Total items: {sum(all_items.values())}")
