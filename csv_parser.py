from resolve import ResolvePokemon, ResolveItemForm, ResolvePPCount
from trainer import TrainerData, TrainerMon
import re
import os
import csv

def list_csv_files(directory):
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".csv")]

def read_csv(file_path):
    with open(file_path, newline='', encoding='utf-8') as f:
        return list(csv.reader(f))

def parse_csv(rows, config):
    trainers = []
    current = None

    for i, row in enumerate(rows):
        if not row or len(row) < 2:
            continue
        key = row[0]

        if key.startswith("Name - "):
            if current is not None:
                trainers.append(current)
            current = TrainerData.create_default(config)

            if config.USE_IV_EV:
                current.trainermontype.add("TRAINER_DATA_TYPE_IV_EV_SET")

            current.id = key.rsplit(" ", 1)[1]
            if not current.id.isdigit():
                current.id = 0

            tags = re.findall(r'\[.*?]', row[1])
            if "[Double]" in tags:
                current.battletype = True

            cleaned_str = re.sub(r'\s*\[.*?\]\s*$', '', row[1])
            words = cleaned_str.split()

            if ' & ' in cleaned_str:
                name_words = 3
            else:
                name_words = 1

            current.name = ' '.join(words[-name_words:])
            current.trainerclass = ' '.join(words[:-name_words])

            continue

        match key:
            case "DV":
                for j, cell in enumerate(row[1:1 + current.nummons]):
                    current.party[j].dv = int(cell)
            case "Ability Slot":
                for j, cell in enumerate(row[1:1 + current.nummons]):
                    current.party[j].abilityslot = int(cell)
            case "Level":
                for j, cell in enumerate(row[1:1 + current.nummons]):
                    current.party[j].level = int(cell)
            case "Pokémon":
                if i + 1 >= len(rows):
                    break
                next_row = rows[i + 1]
                for j, cell in enumerate(next_row[1:]):
                    if cell != '':
                        current.party.append(TrainerMon.create_default(config))
                        if cell.endswith('*'):
                            cell = cell[:-1]
                            current.party[j].shinylock = True
                            current.trainermontype.add("TRAINER_DATA_TYPE_SHINY_LOCK")
                        current.party[j].pokemon = ResolvePokemon(cell)
                        current.nummons += 1
            case "Held Item":
                for j, cell in enumerate(row[1:1 + current.nummons]):
                    if cell != "-" and cell != "":
                        current.party[j].item = cell
                        current.party[j].pokemon, current.party[j].item = ResolveItemForm(current.party[j].pokemon, current.party[j].item)
                current.trainermontype.add("TRAINER_DATA_TYPE_ITEMS")
            case "Moves":
                for k in range(4):
                    if i + k >= len(rows):
                        break
                    move_row = rows[i + k]
                    for j, cell in enumerate(move_row[1:1 + current.nummons]):
                        if cell != "-" and cell != "":
                            current.party[j].move[k], current.party[j].ppcounts[k] = ResolvePPCount(cell)
                            if current.party[j].ppcounts[k] != 0:
                                current.party[j].additionalFlags.append("TRAINER_DATA_EXTRA_TYPE_PP_COUNTS")
                                current.trainermontype.add("TRAINER_DATA_TYPE_ADDITIONAL_FLAGS")
                current.trainermontype.add("TRAINER_DATA_TYPE_MOVES")
            case "Ability":
                for j, cell in enumerate(row[1:1 + current.nummons]):
                    current.party[j].ability = cell
                current.trainermontype.add("TRAINER_DATA_TYPE_ABILITY")
            case "Ball Type":
                for j, cell in enumerate(row[1:1 + current.nummons]):
                    current.party[j].ball = cell
                current.trainermontype.add("TRAINER_DATA_TYPE_BALL")
            case "IVs":
                for j, cell in enumerate(row[1:1 + current.nummons]):
                    current.party[j].setivs = [int(x) for x in cell.split(',')]
                current.trainermontype.add("TRAINER_DATA_TYPE_IV_EV_SET")
            case "EVs":
                for j, cell in enumerate(row[1:1 + current.nummons]):
                    current.party[j].setevs = [int(x) for x in cell.split(',')]
                current.trainermontype.add("TRAINER_DATA_TYPE_IV_EV_SET")
            case "Nature":
                for j, cell in enumerate(row[1:1 + current.nummons]):
                    current.party[j].nature = cell
                current.trainermontype.add("TRAINER_DATA_TYPE_NATURE_SET")
            case "Status":
                for j, cell in enumerate(row[1:1 + current.nummons]):
                    if cell != "-" and cell != "":
                        current.party[j].status = int(cell)
                        current.party[j].additionalFlags.append("TRAINER_DATA_EXTRA_TYPE_STATUS")
                    current.trainermontype.add("TRAINER_DATA_TYPE_ADDITIONAL_FLAGS")
            case "Stats":
                for j, cell in enumerate(row[1:1 + current.nummons]):
                    if cell != '-' and cell != "":
                        current.party[j].stats = [int(x) for x in cell.split(',')]
                        current.party[j].additionalFlags.extend([
                            "TRAINER_DATA_EXTRA_TYPE_HP",
                            "TRAINER_DATA_EXTRA_TYPE_ATK",
                            "TRAINER_DATA_EXTRA_TYPE_DEF",
                            "TRAINER_DATA_EXTRA_TYPE_SPEED",
                            "TRAINER_DATA_EXTRA_TYPE_SP_ATK",
                            "TRAINER_DATA_EXTRA_TYPE_SP_DEF"
                        ])
                    current.trainermontype.add("TRAINER_DATA_TYPE_ADDITIONAL_FLAGS")
            case "Nickname":
                for j, cell in enumerate(row[1:1 + current.nummons]):
                    if cell != "-" and cell != "":
                        current.party[j].nickname = cell
                        current.party[j].additionalFlags.append("TRAINER_DATA_EXTRA_TYPE_NICKNAME")
                    current.trainermontype.add("TRAINER_DATA_TYPE_ADDITIONAL_FLAGS")
            case "Ball Seal":
                for j, cell in enumerate(row[1:1 + current.nummons]):
                    if cell != "-" and cell != "":
                        current.party[j].ballseal = int(cell)
            case "":
                continue
            case _:
                print(f"Unknown Key in Row {i} : {key}")

    if current is not None:
        trainers.append(current)
    return trainers
