from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .image_overlay import create_battle_overlay


@dataclass(frozen=True, slots=True)
class BattleRenderConfig:
    background_path: Path
    enemy_path: Path
    output_path: Path


def handle_bot_command(command: str, config: BattleRenderConfig) -> Optional[Path]:
    """Handle bot commands and return generated image path when applicable."""
    if command.strip().lower() != "!battle":
        return None

    return create_battle_overlay(
        background_path=config.background_path,
        enemy_path=config.enemy_path,
        output_path=config.output_path,
    )
