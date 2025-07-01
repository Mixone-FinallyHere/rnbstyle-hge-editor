import os

class Config:
    def __init__(self, filepath="config.txt"):
        self.filepath = filepath
        self.defaults = {
            "INPUT_DIR": "csv",
            "ROOT_DIR": "../hg-engine/",
            "CREATE_BACKUP": True,
            "DEFAULT_DV": 255,
            "USE_IV_EV": True,
            "DEFAULT_IVS": [31, 31, 31, 31, 31, 31],
            "DEFAULT_EVS": [0, 0, 0, 0, 0, 0],
            "DEFAULT_AI_FLAGS": ["F_PRIORITIZE_SUPER_EFFECTIVE", "F_EVALUATE_ATTACKS", "F_EXPERT_ATTACKS"],
            "DEFAULT_ITEMS": ["ITEM_NONE", "ITEM_NONE", "ITEM_NONE", "ITEM_NONE"],
            "DEFAULT_BALL": "ITEM_POKE_BALL",
            "ADVANCED_MODE": False
        }
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                lines = f.readlines()
            values = {}
            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if '=' in line:
                    key, val = line.split('=', 1)
                    key = key.strip()
                    val = val.strip()
                    try:
                        values[key] = eval(val, {"__builtins__": None}, {})
                    except Exception:
                        values[key] = val.strip('"').strip("'")
        else:
            values = {}
        for k, v in self.defaults.items():
            setattr(self, k, values.get(k, v))

        self._rebuild_paths()

    def save(self, filepath=None):
        filepath = filepath or self.filepath
        with open(filepath, "w") as f:
            for key, default_val in self.defaults.items():
                val = getattr(self, key)
                if isinstance(val, str):
                    val_str = f'"{val}"'
                elif isinstance(val, bool):
                    val_str = "True" if val else "False"
                else:
                    val_str = str(val)
                f.write(f"{key} = {val_str}\n")

    def _rebuild_paths(self):
        self.TRAINER_DIR = self.ROOT_DIR + "armips/data/trainers/"
        self.OUTPUT_FILE = self.TRAINER_DIR + "trainers.s"
        self.BACKUP_FILE = self.TRAINER_DIR + "trainers_backup.s"
        self.INCLUDE_DIR = self.ROOT_DIR + "include/"
        self.CONSTANTS_DIR = self.INCLUDE_DIR + "constants/"
        self.ABILITY_HEADER = self.CONSTANTS_DIR + "ability.h"
        self.ITEM_HEADER = self.CONSTANTS_DIR + "item.h"
        self.MOVE_HEADER = self.CONSTANTS_DIR + "moves.h"
        self.SPECIES_HEADER = self.CONSTANTS_DIR + "species.h"
        self.TRAINERCLASS_HEADER = self.CONSTANTS_DIR + "trainerclass.h"
        self.BATTLE_HEADER = self.INCLUDE_DIR + "battle.h"
        self.POKEMON_HEADER = self.INCLUDE_DIR + "pokemon.h"
