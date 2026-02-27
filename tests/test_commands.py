from pathlib import Path

from battle_system.commands import BattleRenderConfig, handle_bot_command
from battle_system.image_overlay import create_battle_overlay, read_png_rgb, write_png_rgb


def test_create_battle_overlay_places_enemy_on_left(tmp_path: Path):
    bg = tmp_path / "bg.png"
    enemy = tmp_path / "enemy.png"
    out = tmp_path / "out.png"

    # 8x4 blue background
    write_png_rgb(bg, 8, 4, [0, 0, 255] * (8 * 4))

    # 4x2 enemy with black background + red 2x2 block in the middle
    pixels = []
    for y in range(2):
        for x in range(4):
            if 1 <= x <= 2:
                pixels.extend([255, 0, 0])
            else:
                pixels.extend([0, 0, 0])
    write_png_rgb(enemy, 4, 2, pixels)

    create_battle_overlay(
        bg,
        enemy,
        out,
        enemy_scale=1.0,
        enemy_offset_x=1,
        enemy_offset_y=1,
        chroma_key_threshold=20,
    )

    w, h, rgb = read_png_rgb(out)
    assert (w, h) == (8, 4)

    # A red pixel should appear where enemy was placed.
    idx = (1 * 8 + 2) * 3
    assert list(rgb[idx : idx + 3]) == [255, 0, 0]

    # Right side remains untouched blue (reserved player area)
    right_idx = (1 * 8 + 7) * 3
    assert list(rgb[right_idx : right_idx + 3]) == [0, 0, 255]


def test_handle_bot_command_only_triggers_battle(tmp_path: Path):
    bg = tmp_path / "bg.png"
    enemy = tmp_path / "enemy.png"
    out = tmp_path / "out.png"

    write_png_rgb(bg, 2, 2, [30, 60, 90] * 4)
    write_png_rgb(enemy, 2, 2, [200, 20, 20] * 4)

    config = BattleRenderConfig(background_path=bg, enemy_path=enemy, output_path=out)

    assert handle_bot_command("!status", config) is None
    result = handle_bot_command("!battle", config)
    assert result == out
    assert out.exists()
