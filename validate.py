import os

from models import ItemClassification, load_datapackage
from utils import world_folder

valid_classifications = set(ItemClassification.__members__.keys())

def validate_world(world_name) -> None:
    world_path = world_folder / world_name
    progression_txt = world_path / "progression.txt"
    if not progression_txt.exists():
        raise FileNotFoundError(f"progression.txt not found in {world_name}")
    dp = load_datapackage(world_name)
    assert dp.items, f"datapackage for {world_name} is empty"

for world in os.listdir(world_folder):
    validate_world(world)
