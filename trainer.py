from dataclasses import dataclass, field
from typing import List, Set, Tuple

@dataclass
class TrainerMon:
    dv: int
    abilityslot: int
    level: int
    pokemon: Tuple[str, int]
    item: str
    move: List[str]
    ability: str
    ball: str
    setivs: List[int]
    setevs: List[int]
    nature: str
    shinylock: bool
    additionalFlags: List[str]
    status: int
    stats: List[int]
    ppcounts: List[int]
    nickname: str
    ballseal: int

    @classmethod
    def create_default(cls, config):
        return cls(
            dv=config.DEFAULT_DV,
            abilityslot=0,
            level=0,
            pokemon=("SPECIES_NONE", 0),
            item="ITEM_NONE",
            move=["MOVE_NONE", "MOVE_NONE", "MOVE_NONE", "MOVE_NONE"],
            ability="ABILITY_NONE",
            ball=config.DEFAULT_BALL,
            setivs=config.DEFAULT_IVS.copy(),
            setevs=config.DEFAULT_EVS.copy(),
            nature="NATURE_HARDY",
            shinylock=False,
            additionalFlags=[],
            status=0x0,
            stats=[0, 0, 0, 0, 0, 0],
            ppcounts=[0, 0, 0, 0],
            nickname="",
            ballseal=0
        )


@dataclass
class TrainerData:
    id: int
    name: str
    trainermontype: Set[str]
    trainerclass: str
    nummons: int
    item: List[str]
    aiflags: Set[str]
    battletype: bool
    party: List[TrainerMon]

    @classmethod
    def create_default(cls, config):
        return cls(
            id=0,
            name="",
            trainermontype=set(),
            trainerclass="Ethan",
            nummons=0,
            item=config.DEFAULT_ITEMS.copy(),
            aiflags=set(config.DEFAULT_AI_FLAGS),
            battletype=False,
            party=[]
        )
