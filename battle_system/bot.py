from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

from .commands import BattleRenderConfig, handle_bot_command


@dataclass(frozen=True, slots=True)
class BotRuntimeConfig:
    token: str
    background_path: Path
    enemy_path: Path
    output_path: Path


DEFAULT_OUTPUT_PATH = Path("generated/battle.png")


def load_runtime_config_from_env() -> BotRuntimeConfig:
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise ValueError("Missing DISCORD_BOT_TOKEN environment variable")

    background = os.getenv("BATTLE_BACKGROUND_PATH")
    if not background:
        raise ValueError("Missing BATTLE_BACKGROUND_PATH environment variable")

    enemy = os.getenv("BATTLE_ENEMY_PATH")
    if not enemy:
        raise ValueError("Missing BATTLE_ENEMY_PATH environment variable")

    output = os.getenv("BATTLE_OUTPUT_PATH", str(DEFAULT_OUTPUT_PATH))

    return BotRuntimeConfig(
        token=token,
        background_path=Path(background),
        enemy_path=Path(enemy),
        output_path=Path(output),
    )


def run_discord_bot(config: BotRuntimeConfig) -> None:
    import discord

    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    render_config = BattleRenderConfig(
        background_path=config.background_path,
        enemy_path=config.enemy_path,
        output_path=config.output_path,
    )

    @client.event
    async def on_ready() -> None:
        logging.info("Logged in as %s", client.user)

    @client.event
    async def on_message(message: discord.Message) -> None:
        if message.author == client.user:
            return

        image_path = handle_bot_command(message.content, render_config)
        if image_path is None:
            return

        await message.channel.send(file=discord.File(str(image_path)))

    client.run(config.token)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    runtime_config = load_runtime_config_from_env()
    run_discord_bot(runtime_config)


if __name__ == "__main__":
    main()
