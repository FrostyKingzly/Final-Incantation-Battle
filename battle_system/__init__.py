"""Core domain models and battle engine primitives for Final Incantation."""

from .commands import BattleRenderConfig, handle_bot_command
from .engine import BattleState, TurnManager
from .models import (
    Character,
    DamageProfile,
    DamageType,
    DragonProfile,
    Element,
    LinkChain,
    Party,
    Skill,
    Weapon,
)

__all__ = [
    "BattleState",
    "TurnManager",
    "Character",
    "DamageProfile",
    "DamageType",
    "DragonProfile",
    "Element",
    "LinkChain",
    "Party",
    "Skill",
    "Weapon",
    "BattleRenderConfig",
    "handle_bot_command",
]
