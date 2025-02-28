import os

from models import ItemClassification
from utils import world_folder, load_progressions

valid_classifications = set(ItemClassification.__members__.keys())

def validate_world(world_name):
    errors = []
    world_path = world_folder / world_name
    progression_txt = world_path / "progression.txt"
    if not progression_txt.exists():
        raise FileNotFoundError(f"progression.txt not found in {world_name}")
    items = load_progressions(world_name)
    for name, classification in items.items():
        if classification not in valid_classifications:
            errors.append(f"{name} has invalid classification {classification}")
    if errors:
        raise ValueError(f"Errors in {world_name}:\n" + "\n".join(errors))
    return True

for world in os.listdir(world_folder):
    validate_world(world)
