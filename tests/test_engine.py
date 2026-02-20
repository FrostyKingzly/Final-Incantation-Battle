from battle_system.engine import BattleState, TurnManager
from battle_system.models import (
    Character,
    DamageProfile,
    DamageType,
    DragonProfile,
    Element,
    Party,
    Skill,
    Weapon,
)


def make_character(name: str, speed: int, is_dragon: bool = False) -> Character:
    weapon = Weapon(
        name="Starter Weapon",
        description="Basic weapon",
        base_element=Element.FIRE,
        base_damage_type=DamageType.PHYSICAL,
    )
    strike = Skill(
        name="Strike",
        description="Deals damage",
        damage=DamageProfile(element=Element.FIRE, damage_type=DamageType.PHYSICAL),
    )
    ult = Skill(
        name="Final Burst",
        description="Big hit",
        damage=DamageProfile(element=Element.WIND, damage_type=DamageType.MAGIC),
    )
    follow_up = Skill(name="Counter", description="Follow-up")

    dragon_profile = None
    if is_dragon:
        dragon_profile = DragonProfile(
            transform_name="Paradaemon Form",
            criteria="Break 3 enemies",
            team_buff_description="+20% damage raidwide",
            awakened_passive="+10% team crit",
        )

    return Character(
        name=name,
        speed=speed,
        weapon=weapon,
        passive="Passive",
        skills=[strike],
        ultimate=ult,
        follow_up=follow_up,
        link_effect="Boost",
        is_dragon=is_dragon,
        dragon_profile=dragon_profile,
    )


def test_speed_affects_turn_order():
    fast = make_character("Fast", 200)
    slow = make_character("Slow", 100)

    tm = TurnManager([fast, slow])
    assert tm.next_actor().name == "Fast"


def test_ultimate_charges_allies_and_creates_link_chain():
    a = make_character("A", 120)
    b = make_character("B", 110)
    a.ult_charge = 100

    party = Party(name="P1", active=[a, b])
    state = BattleState([party])
    chain = state.use_ultimate(a, [a, b])

    assert b.ult_charge == 25
    assert chain.final_element == Element.WIND
    assert chain.total_links == 1


def test_dragon_transform():
    d = make_character("Dragon", 90, is_dragon=True)
    party = Party(name="P1", active=[d])
    state = BattleState([party])

    buff_text = state.trigger_dragon_transform(d)
    assert d.transformed is True
    assert "damage" in buff_text
