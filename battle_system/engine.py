from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List

from .models import Character, LinkChain, Party


def initial_action_value(speed: int, base: int = 10000) -> int:
    """Lower AV means earlier turn. Higher speed lowers AV."""
    return max(1, base // max(1, speed))


@dataclass(slots=True)
class TurnManager:
    characters: List[Character]
    av_map: Dict[str, int] = field(init=False)

    def __post_init__(self) -> None:
        self.av_map = {c.name: initial_action_value(c.speed) for c in self.characters}

    def next_actor(self) -> Character:
        actor_name = min(self.av_map, key=self.av_map.get)
        actor = next(c for c in self.characters if c.name == actor_name)
        # after acting, actor's AV is reset; all others count down by actor's AV value
        elapsed = self.av_map[actor_name]
        for key in self.av_map:
            self.av_map[key] = max(0, self.av_map[key] - elapsed)
        self.av_map[actor_name] = initial_action_value(actor.speed)
        return actor


@dataclass(slots=True)
class BattleState:
    parties: List[Party]
    turn_manager: TurnManager = field(init=False)

    def __post_init__(self) -> None:
        roster = list(self.iter_active_characters())
        self.turn_manager = TurnManager(roster)

    def iter_active_characters(self) -> Iterable[Character]:
        for party in self.parties:
            yield from party.active

    def use_ultimate(self, actor: Character, allies: List[Character]) -> LinkChain:
        if not actor.spend_ult_charge():
            raise ValueError(f"{actor.name} does not have a full ultimate charge")

        for ally in allies:
            if ally is not actor:
                ally.gain_ult_charge(25)

        return LinkChain(initiator=actor)

    def trigger_dragon_transform(self, actor: Character) -> str:
        if not actor.can_transform():
            raise ValueError("Dragon transform unavailable")
        actor.transformed = True
        return actor.dragon_profile.team_buff_description  # type: ignore[union-attr]
