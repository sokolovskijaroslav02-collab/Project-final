from typing import Dict, List, Callable, Optional
from combat_system import Character, WEAPONS, ARMORS

# Определение противников
ENEMIES = {
    "mimic": Character("Мимик", 25, 25, WEAPONS["rusty_sword"], ARMORS["leather"], 0.1),
    "skeleton": Character("Скелет", 20, 20, WEAPONS["rusty_sword"], ARMORS["leather"], 0.1),
    "giant_spider": Character("Гигантский паук", 18, 18, WEAPONS["rusty_sword"], ARMORS["leather"], 0.2),
    "owlbear": Character("Совомед", 35, 35, WEAPONS["iron_sword"], ARMORS["chainmail"], 0.05),
    "ervan_human": Character("Эрван (человек)", 40, 40, WEAPONS["steel_blade"], ARMORS["plate_armor"], 0.15),
    "ervan_wizard": Character("Эрван Душегуб", 50, 50, WEAPONS["dragon_slayer"], ARMORS["legendary_armor"], 0.2),
    "dragon": Character("Пеплорёв - Красный дракон", 80, 80, WEAPONS["dragon_slayer"], ARMORS["dragon_scale"], 0.1),
}

def get_tavern_scene(session) -> Dict:
    """Сцена 1: Таверна «На виду»"""
    # Определяем, какое изображение показывать
    if session.get_flag("ervan_revealed"):
        image = "evil1.png"
    else:
        image = "tower1.png"
    
    text = """Дверь в подсобку распахивается, и из неё выходит трактирщик, приветствуя вас.
«О, боюсь, вы пришли не вовремя! Мы закрыты на ремонт. Но чтобы помочь вам в вашем путешествии, 
я с удовольствием приготовлю для вас острые крылышки». Трактирщик представляется как Весельчак Доброром."""
    
    buttons = [
        {"title": "🍗 Согласиться на крылышки", "action": "agree_wings"},
        {"title": "🔍 Осмотреть бар", "action": "search_bar"},
        {"title": "🏠 Подняться наверх", "action": "go_upstairs"},
        {"title": "⚔️ Напасть на трактирщика", "action": "attack_bartender"},
    ]
    
    return {"text": text, "image": image, "buttons": buttons, "scene": "tavern"}

def get_meadow_scene(session) -> Dict:
    """Сцена 2: Луг"""
    text = """Вокруг разрушенной башни, увитой колючим плющом, раскинулся пышный луг. 
Рядом с руинами растет огромное дерево. По лугу ползком крадется совомед, охотясь на трех гигантских пауков."""
    
    buttons = [
        {"title": "🌳 Подойти к дереву", "action": "approach_tree"},
        {"title": "🕷️ Сразиться с пауками", "action": "fight_spiders"},
        {"title": "🍄 Исследовать грибы под мостом", "action": "investigate_mushrooms"},
        {"title": "🌿 Вернуться в таверну", "action": "back_to_tavern"},
    ]
    
    return {"text": text, "image": "tower1.png", "buttons": buttons, "scene": "meadow"}

def get_dungeon_scene(session) -> Dict:
    """Сцена 3: Подземелье"""
    text = """Вход в это затхлое подземелье освещён факелами. К одной из стен прислонился безголовый скелет.
По полу подземелья ползают три черных сгустка слизи. В воздухе парят несколько предметов: светящийся желтый драгоценный камень, череп и посеребренная сковорода."""
    
    buttons = [
        {"title": "⚔️ Сразиться со слизью", "action": "fight_slime"},
        {"title": "🔍 Осмотреть скелет", "action": "inspect_skeleton"},
        {"title": "🗝️ Искать путь к камере", "action": "find_cell_door"},
        {"title": "⬆️ Вернуться на луг", "action": "back_to_meadow"},
    ]
    
    return {"text": text, "image": "tower1.png", "buttons": buttons, "scene": "dungeon"}

# Карта сцен для навигации
SCENES = {
    "tavern": get_tavern_scene,
    "meadow": get_meadow_scene,
    "dungeon": get_dungeon_scene,
    "basement": lambda s: {"text": "Подвал башни...", "image": "tower1.png", "buttons": [], "scene": "basement"},
    "tower": lambda s: {"text": "Башня...", "image": "tower2.png", "buttons": [], "scene": "tower"},
    "dragon": lambda s: {"text": "Финальная битва с драконом!", "image": "dragon.png", "buttons": [], "scene": "dragon"},
}
