from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class Element(str, Enum):
    FIRE = "fire"
    WATER = "water"
    WIND = "wind"
    EARTH = "earth"
    LIGHTNING = "lightning"
    LIGHT = "light"
    DARK = "dark"
    ARCANE = "arcane"


class DamageType(str, Enum):
    PHYSICAL = "physical"
    MAGIC = "magic"


@dataclass(slots=True)
class DamageProfile:
    element: Element
    damage_type: DamageType
    power_ratio: float = 1.0


@dataclass(slots=True)
class Skill:
    name: str
    description: str
    damage: Optional[DamageProfile] = None
    status_only: bool = False


@dataclass(slots=True)
class Weapon:
    name: str
    description: str
    base_element: Element
    base_damage_type: DamageType
    gem_effect: Optional[str] = None


@dataclass(slots=True)
class DragonProfile:
    transform_name: str
    criteria: str
    team_buff_description: str
    awakened_passive: Optional[str] = None


@dataclass(slots=True)
class Character:
    name: str
    speed: int
    weapon: Weapon
    passive: str
    skills: List[Skill]
    ultimate: Skill
    follow_up: Skill
    link_effect: str
    is_dragon: bool = False
    dragon_profile: Optional[DragonProfile] = None
    hp: int = 1000
    ult_charge: int = 0
    transformed: bool = False

    def can_transform(self) -> bool:
        return bool(self.is_dragon and self.dragon_profile and not self.transformed)

    def gain_ult_charge(self, amount: int) -> None:
        self.ult_charge = min(100, self.ult_charge + amount)

    def spend_ult_charge(self) -> bool:
        if self.ult_charge < 100:
            return False
        self.ult_charge = 0
        return True


@dataclass(slots=True)
class Party:
    name: str
    active: List[Character] = field(default_factory=list)
    bench: List[Character] = field(default_factory=list)
    max_active: int = 4

    def add_active(self, character: Character) -> None:
        if len(self.active) >= self.max_active:
            raise ValueError("Active party is full")
        self.active.append(character)

    def swap_with_bench(self, active_index: int, bench_index: int) -> None:
        if active_index >= len(self.active) or bench_index >= len(self.bench):
            raise IndexError("Invalid swap indices")
        self.active[active_index], self.bench[bench_index] = (
            self.bench[bench_index],
            self.active[active_index],
        )


@dataclass(slots=True)
class LinkChain:
    initiator: Character
    participants: List[Character] = field(default_factory=list)

    def add_link(self, character: Character) -> None:
        if character in self.participants:
            return
        self.participants.append(character)

    @property
    def total_links(self) -> int:
        return len(self.participants) + 1

    @property
    def final_element(self) -> Element:
        if not self.initiator.ultimate.damage:
            return self.initiator.weapon.base_element
        return self.initiator.ultimate.damage.element

    @property
    def damage_multiplier(self) -> float:
        # Base 1.0 + 0.5 per additional linker
        return 1.0 + (0.5 * (self.total_links - 1))

    @property
    def full_link(self) -> bool:
        return self.total_links >= 4
