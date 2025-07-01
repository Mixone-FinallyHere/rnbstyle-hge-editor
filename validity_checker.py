# validity_checker.py
from typing import List, Tuple, Set
from header_parser import extract_defines
from trainer import TrainerData, TrainerMon

abilityDefines = []
battleDefines = []
itemDefines = []
moveDefines = []
pokemonDefines  = []
speciesDefines = []
trainerClassDefines = []

def init_defines(config):
    global abilityDefines
    global battleDefines
    global itemDefines
    global moveDefines
    global pokemonDefines
    global speciesDefines
    global trainerClassDefines

    abilityDefines = extract_defines(config.ABILITY_HEADER)
    battleDefines = extract_defines(config.BATTLE_HEADER)
    itemDefines = extract_defines(config.ITEM_HEADER)
    moveDefines = extract_defines(config.MOVE_HEADER)
    pokemonDefines = extract_defines(config.POKEMON_HEADER)
    speciesDefines = extract_defines(config.SPECIES_HEADER)
    trainerClassDefines = extract_defines(config.TRAINERCLASS_HEADER)

def CheckTrainerValidity(trainer):
    CheckTrainerParamValidity(trainer.trainermontype, pokemonDefines)
    CheckTrainerParamValidity(trainer.trainerclass, trainerClassDefines)
    CheckTrainerParamValidity(trainer.item, itemDefines)

    for mon in trainer.party:
        CheckTrainerParamValidity(mon.pokemon[0], speciesDefines)
        CheckTrainerParamValidity(mon.item, itemDefines)
        CheckTrainerParamValidity(mon.move, moveDefines)
        CheckTrainerParamValidity(mon.ability, abilityDefines)
        CheckTrainerParamValidity(mon.ball, itemDefines)
        CheckTrainerParamValidity(mon.nature, pokemonDefines)
        CheckTrainerParamValidity(mon.additionalFlags, pokemonDefines)


def CheckTrainerParamValidity(param, defines):
    if isinstance(param, (list, set, tuple)):
        for obj in param:
            if obj not in defines:
                print(f"Unknown value : {obj}")
    elif param not in defines:
        print(f"Unknown value : {param}")
