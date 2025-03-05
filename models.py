import enum

import attrs
from utils import world_folder
import re
import yaml

class ItemClassification(enum.Flag):
    unknown = 0
    trap = 1
    filler = 2
    useful = 4
    progression = 8
    mcguffin = 16

    bad_name = 256

classifications = {v.name: v for v in ItemClassification.__members__.values()}

@attrs.define()
class Datapackage:
    items: dict[str, ItemClassification] = attrs.field(factory=dict)
    categories: dict[str, ItemClassification] = attrs.field(factory=dict)

    def icon(self, item_name: str) -> str:
        classification = self.items.get(item_name, ItemClassification.unknown)
        emoji = "❓"
        if classification == ItemClassification.mcguffin:
            emoji = "✨"
        if classification == ItemClassification.filler:
            emoji = "<:filler:1277502385459171338>"
        if classification == ItemClassification.useful:
            emoji = "<:useful:1277502389729103913>"
        if classification == ItemClassification.progression:
            emoji = "<:progression:1277502382682542143>"
        if classification == ItemClassification.trap:
            emoji = "❌"
        return emoji


def load_datapackage(game_name, dp: Datapackage = None) -> Datapackage:
    if dp is None:
        dp = Datapackage()
    info_yaml = world_folder.joinpath(game_name, "info.yaml")
    if info_yaml.exists():
        info = yaml.safe_load(info_yaml)
        if 'items' in info:
            for name, classification in info['items'].items():
                dp.items[name] = classifications[classification.strip()]

    prog_txt = world_folder.joinpath(game_name, "progression.txt")
    if prog_txt.exists():
        progressionFile = open(prog_txt, "r", encoding="utf-8")
        text = progressionFile.read()
        progressionFile.close()
        for x in text.splitlines():
            if not x:
                continue
            match = re.match(r"^(.*): (.*)$", x)
            dp.items[match[1]] = classifications[match[2].strip()]
    categories_txt = world_folder.joinpath(game_name, "categories.txt")
    if categories_txt.exists():
        categoriesFile = open(categories_txt, "r", encoding="utf-8")
        text = categoriesFile.read()
        categoriesFile.close()
        for x in text.splitlines():
            if not x:
                continue
            match = re.match(r"^(.*): (.*)$", x)
            dp.categories[match[1]] = classifications[match[2].strip()]

    return dp

def save_datapackage(game_name, dp: Datapackage) -> None:
    info = {}
    for name, classification in dp.items.items():
        info[name] = classification.name
    if dp.categories:
        save_complex(game_name, dp, info)
        return

    progressionFile = world_folder.joinpath(game_name, "progression.txt")
    progressionFile.write_text("\n".join([f"{k}: {v.name}" for k, v in dp.items.items()]))

    return dp

def save_complex(game_name, dp: Datapackage, info: dict[str, ItemClassification]) -> None:
    dump = yaml.dump({"categories": dp.categories, "items": info})
    world_folder.joinpath(game_name, "info.yaml").write_text(dump)
    progressionFile = world_folder.joinpath(game_name, "progression.txt")
    if progressionFile.exists():
        progressionFile.unlink()
