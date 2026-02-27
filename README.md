# Final Incantation Battle Bot (Foundations)

This repository contains a first-pass Python rules engine for the battle concepts you described for a Discord RPG bot.

## What's implemented

- Core combat entities:
  - Characters with unique weapon, skills, ultimate, passive, follow-up, and link profile
  - Damage metadata (`element`, `damage_type`)
  - Dragon-specific transformation profile and awakened passive support
- Party model with configurable roster limits:
  - Active lineup (`max_active` default `4`)
  - Optional bench/backline support
- Turn-order system based on **Action Value (AV)** countdown:
  - Faster units get lower AV and can act more often
- Link ultimate flow primitives:
  - Ult use grants charge to allies
  - Link chains can be built and resolved
  - Final link element determined by link initiator
- Lightweight battle state container for future Discord command integration
- Simple bot command stub for image battles:
  - `!battle` composites a configured background + enemy image
  - Enemy is positioned on the left to leave room for player characters on the right
  - Image paths are provided at runtime (`BattleRenderConfig`) to avoid committing binary assets
- Runnable Discord bot entrypoint:
  - Reads token + image paths from environment variables
  - Logs in and responds to `!battle` by generating and posting the rendered image

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pytest
```

## Run the bot

Set the required environment variables and then start the bot with either the module form or installed command:

```bash
export DISCORD_BOT_TOKEN="your-token-here"
export BATTLE_BACKGROUND_PATH="/absolute/path/to/background.png"
export BATTLE_ENEMY_PATH="/absolute/path/to/enemy.png"
# optional; defaults to generated/battle.png
export BATTLE_OUTPUT_PATH="/absolute/path/to/output.png"

python -m battle_system.bot
# or: final-incantation-bot
```

Then in Discord, send `!battle` in a channel the bot can read/write.

## Next steps

- Add status effect engine (DoT, break, resist, debuffs)
- Implement follow-up trigger conditions as an event bus
- Add raid session orchestration (multiple parties, shared boss)
- Integrate with a Discord bot framework (`discord.py`/`py-cord`)
