import pytest

from battle_system.bot import DEFAULT_OUTPUT_PATH, load_runtime_config_from_env


def test_load_runtime_config_from_env_success(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "abc123")
    monkeypatch.setenv("BATTLE_BACKGROUND_PATH", "assets/bg.png")
    monkeypatch.setenv("BATTLE_ENEMY_PATH", "assets/enemy.png")

    config = load_runtime_config_from_env()

    assert config.token == "abc123"
    assert str(config.background_path) == "assets/bg.png"
    assert str(config.enemy_path) == "assets/enemy.png"
    assert config.output_path == DEFAULT_OUTPUT_PATH


@pytest.mark.parametrize(
    "missing_var",
    ["DISCORD_BOT_TOKEN", "BATTLE_BACKGROUND_PATH", "BATTLE_ENEMY_PATH"],
)
def test_load_runtime_config_from_env_missing_required(monkeypatch, missing_var):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "abc123")
    monkeypatch.setenv("BATTLE_BACKGROUND_PATH", "assets/bg.png")
    monkeypatch.setenv("BATTLE_ENEMY_PATH", "assets/enemy.png")

    monkeypatch.delenv(missing_var)

    with pytest.raises(ValueError):
        load_runtime_config_from_env()
