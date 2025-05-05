import enum
import os
import pathlib

import attrs
import re
import yaml

abspath = os.path.dirname(__file__)
world_folder = pathlib.Path(abspath, "worlds")

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
    game_name: str = attrs.field(default="")

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

    def set_classification(self, item_name: str, classification: ItemClassification) -> bool:
        if classification == ItemClassification.unknown and self.items.get(item_name, ItemClassification.unknown) != ItemClassification.unknown:
            # We don't want to set an item to unknown if it's already classified
            return False
        if self.items.get(item_name) == classification:
            return False
        self.items[item_name] = classification
        return True


def load_datapackage(game_name, dp: Datapackage = None, follow_redirect: bool = True) -> Datapackage:
    if dp is None:
        dp = Datapackage()
    game_name = game_name.replace("/", "_").replace(":", "_")
    if os.path.exists(world_folder.joinpath(game_name, "redirect.txt")) and follow_redirect:
        game_name = world_folder.joinpath(game_name, "redirect.txt").read_text().strip()
    dp.game_name = game_name

    info_yaml = world_folder.joinpath(game_name, "info.yaml")
    if info_yaml.exists():
        info = yaml.safe_load(info_yaml)
        if 'items' in info:
            for name, classification in info['items'].items():
                dp.set_classification(name, classifications[classification.strip()])

    prog_txt = world_folder.joinpath(game_name, "progression.txt")
    if prog_txt.exists():
        try:
            progressionFile = open(prog_txt, "r", encoding="utf-8", errors="backslashreplace")
            text = progressionFile.read()
            progressionFile.close()
        except UnicodeDecodeError as e:
            print(f"Error reading {prog_txt}: {e}")
            raise

        for x in text.splitlines():
            if not x:
                continue
            match = re.match(r"^(.*): (.*)$", x)
            dp.set_classification(match[1], classifications[match[2].strip()])

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
    game_name = game_name.replace("/", "_").replace(":", "_")
    if os.path.exists(world_folder.joinpath(game_name, "redirect.txt")):
        game_name = world_folder.joinpath(game_name, "redirect.txt").read_text().strip()
    info = {}
    for name, classification in dp.items.items():
        info[name] = classification.name
    if dp.categories:
        save_complex(game_name, dp, info)
        return

    world_folder.joinpath(game_name).mkdir(parents=True, exist_ok=True)
    progressionFile = world_folder.joinpath(game_name, "progression.txt")
    lines = [f"{k}: {v.name}" for k, v in dp.items.items()]
    lines.sort()
    progressionFile.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return dp

def save_complex(game_name, dp: Datapackage, info: dict[str, ItemClassification]) -> None:
    dump = yaml.dump({"categories": dp.categories, "items": info})
    world_folder.joinpath(game_name, "info.yaml").write_text(dump, encoding="utf-8")
    progressionFile = world_folder.joinpath(game_name, "progression.txt")
    if progressionFile.exists():
        progressionFile.unlink()
