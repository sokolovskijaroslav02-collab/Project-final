import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class Weapon:
    name: str
    damage_min: int
    damage_max: int
    crit_chance: float = 0.1
    icon: str = "⚔️"

@dataclass
class Armor:
    name: str
    defense: int
    block_chance: float
    icon: str = "🛡️"

@dataclass
class Character:
    name: str
    hp: int
    max_hp: int
    weapon: Weapon
    armor: Armor
    evasion_chance: float = 0.2
    level: int = 1
    
    @property
    def is_alive(self) -> bool:
        return self.hp > 0
    
    def take_damage(self, damage: int) -> int:
        """Возвращает фактический полученный урон"""
        actual_damage = max(0, damage - self.armor.defense)
        self.hp -= actual_damage
        return actual_damage
    
    def heal(self, amount: int) -> int:
        healed = min(amount, self.max_hp - self.hp)
        self.hp += healed
        return healed

class CombatSystem:
    """Управляет боем с уклонением, блоками и критическими ударами"""
    
    def __init__(self):
        self.combat_log: List[str] = []
    
    def clear_log(self):
        self.combat_log = []
    
    def calculate_damage(self, attacker: Character, defender: Character) -> Tuple[int, str]:

        # Проверка уклонения
        if random.random() < defender.evasion_chance:
            msg = f"💨 {defender.name} уклонился от атаки!"
            self.combat_log.append(msg)
            return 0, msg
        
        # Базовая атака
        base_damage = random.randint(attacker.weapon.damage_min, attacker.weapon.damage_max)
        
        # Критический удар
        is_crit = random.random() < attacker.weapon.crit_chance
        if is_crit:
            base_damage = int(base_damage * 1.5)
            crit_msg = " 💥 КРИТИЧЕСКИЙ УДАР!"
        else:
            crit_msg = ""
        
        # Проверка блока брони
        if random.random() < defender.armor.block_chance:
            blocked_damage = int(base_damage * 0.5)
            actual_damage = defender.take_damage(blocked_damage)
            msg = f"🛡️ {defender.name} заблокировал атаку! Получено {actual_damage} урона{crit_msg}"
            self.combat_log.append(msg)
            return actual_damage, msg
        
        actual_damage = defender.take_damage(base_damage)
        msg = f"{attacker.weapon.icon} {attacker.name} атакует {defender.name} и наносит {actual_damage} урона{crit_msg}"
        self.combat_log.append(msg)
        return actual_damage, msg
    
    def player_attack(self, player: Character, enemy: Character) -> str:
        """Атака игрока на врага"""
        damage, msg = self.calculate_damage(player, enemy)
        
        if not enemy.is_alive:
            msg += f"\n✨ {enemy.name} повержен!"
            self.combat_log.append(msg)
        return msg
    
    def enemy_attack(self, enemy: Character, player: Character) -> str:
        """Атака врага на игрока"""
        damage, msg = self.calculate_damage(enemy, player)
        
        if not player.is_alive:
            msg += f"\n💀 {player.name} пал в бою..."
            self.combat_log.append(msg)
        return msg
    
    def get_log(self) -> List[str]:
        return self.combat_log.copy()

# Предопределенное оружие и броня (чем мощнее — тем лучше)
WEAPONS = {
    "rusty_sword": Weapon("Ржавый меч", 3, 7, 0.05, "🗡️"),
    "iron_sword": Weapon("Железный меч", 5, 10, 0.10, "⚔️"),
    "steel_blade": Weapon("Стальной клинок", 8, 14, 0.12, "🗡️"),
    "dragon_slayer": Weapon("Драконоборец", 15, 25, 0.20, "🐉⚔️"),
    "hero_sword": Weapon("Меч героя", 12, 20, 0.15, "✨⚔️"),
}

ARMORS = {
    "leather": Armor("Кожаная броня", 1, 0.05, "🥋"),
    "chainmail": Armor("Кольчуга", 3, 0.10, "⛓️"),
    "plate_armor": Armor("Латы", 5, 0.15, "🛡️"),
    "dragon_scale": Armor("Чешуя дракона", 8, 0.25, "🐉🛡️"),
    "legendary_armor": Armor("Легендарный доспех", 10, 0.30, "✨🛡️"),
}
