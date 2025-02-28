import os
from os.path import join
import re
import pathlib

abspath = os.path.dirname(__file__)
world_folder = pathlib.Path(abspath, "worlds")

def load_progressions(game_name) -> dict[str, str]:
    items = {}
    try:
        progressionFile = open(world_folder / game_name / "progression.txt", "r", encoding="utf-8")
        text = progressionFile.read()
        progressionFile.close()
        for x in text.splitlines():
            if not x:
                continue
            match = re.match(r"(.*): (.*)", x)
            items[match[1]] = match[2].strip()
    except FileNotFoundError:
        pass
    return items
