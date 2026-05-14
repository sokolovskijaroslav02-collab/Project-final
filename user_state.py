from typing import Dict, Optional
from combat_system import Character, Weapon, Armor, WEAPONS, ARMORS

class UserSession:
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.current_scene: str = "tavern"  
        self.step: int = 0
        self.inventory: list = []
        self.flags: Dict[str, bool] = {} 
        self.character: Optional[Character] = None
        self.combat_active: bool = False
        self.current_enemy: Optional[Character] = None
        self.alexa_image: Optional[str] = None 
        
    @classmethod
    def create_new_hero(cls, user_id: str) -> "UserSession":
        """Создает нового героя с начальной экипировкой"""
        session = cls(user_id)
        session.character = Character(
            name="Рыцарь",
            hp=30,
            max_hp=30,
            weapon=WEAPONS["iron_sword"],
            armor=ARMORS["chainmail"],
            evasion_chance=0.15,
            level=1
        )
        session.inventory = ["зелье_лечения", "хлеб"]
        return session
    
    def set_flag(self, flag_name: str, value: bool = True):
        self.flags[flag_name] = value
    
    def get_flag(self, flag_name: str) -> bool:
        return self.flags.get(flag_name, False)

# Хранилище сессий 
sessions: Dict[str, UserSession] = {}

def get_session(user_id: str) -> Optional[UserSession]:
    return sessions.get(user_id)

def create_session(user_id: str) -> UserSession:
    session = UserSession.create_new_hero(user_id)
    sessions[user_id] = session
    return session
