import json
import uuid
from flask import Flask, request, jsonify, render_template
from flask_session import Session
from user_state import get_session, create_session, sessions
from story_data import SCENES, ENEMIES, get_tavern_scene
from combat_system import CombatSystem

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Глобальный экземпляр системы боя
combat_system = CombatSystem()

def build_alice_response(text: str, session_state: dict, buttons: list = None, image_url: str = None, end_session: bool = False) -> dict:
    """
    Формирует ответ для Яндекс.Алисы с поддержкой кнопок и изображений
    """
    response = {
        "text": text,
        "tts": text,
        "end_session": end_session
    }
    
    # Добавляем кнопки
    if buttons:
        response["buttons"] = [
            {"title": btn["title"], "payload": {"action": btn["action"]}}
            for btn in buttons
        ]
    
    # Добавляем изображение для устройств с экраном
    if image_url:
        response["card"] = {
            "type": "BigImage",
            "image_id": image_url,
            "title": "Приключение"
        }
    
    return {
        "response": response,
        "session_state": session_state,
        "version": "1.0"
    }

def handle_combat_turn(session, user_action: str, message_text: str) -> dict:
    """Обрабатывает ход боя"""
    player = session.character
    enemy = session.current_enemy
    
    if not player or not enemy:
        session.combat_active = False
        return None
    
    if user_action == "attack":
        result = combat_system.player_attack(player, enemy)
        if not enemy.is_alive:
            session.combat_active = False
            session.current_enemy = None
            session.set_flag("enemy_defeated", True)
            return build_alice_response(
                f"{result}\n\nПротивник повержен! Что дальше?",
                {"scene": session.current_scene, "step": session.step},
                [{"title": "Продолжить", "action": "continue"}],
                "hero1.png"
            )
        
        # Ответный ход врага
        enemy_result = combat_system.enemy_attack(enemy, player)
        
        if not player.is_alive:
            return build_alice_response(
                f"{result}\n{enemy_result}\n\n💀 Вы погибли в бою. Игра окончена.",
                {"scene": "game_over"},
                [{"title": "Начать заново", "action": "restart"}],
                "hero1.png",
                end_session=True
            )
        
        return build_alice_response(
            f"{result}\n{enemy_result}\n\nВаше HP: {player.hp}/{player.max_hp} | HP врага: {enemy.hp}/{enemy.max_hp}",
            {"scene": session.current_scene, "combat_active": True, "step": session.step},
            [
                {"title": "⚔️ Атаковать", "action": "attack"},
                {"title": "🏃 Сбежать", "action": "flee"}
            ],
            "hero1.png"
        )
    
    elif user_action == "flee":
        session.combat_active = False
        session.current_enemy = None
        return build_alice_response(
            "Вы убежали с поля боя и вернулись в безопасное место.",
            {"scene": session.current_scene, "step": session.step},
            [{"title": "Продолжить", "action": "continue"}],
            "hero1.png"
        )
    
    return None

@app.route('/alice', methods=['POST'])
def alice_webhook():
    """
    Основной обработчик запросов от Яндекс.Алисы
    """
    req = request.get_json()
    
    # Получаем ID пользователя и сессию
    user_id = req.get('session', {}).get('user', {}).get('user_id', str(uuid.uuid4()))
    session_data = req.get('state', {}).get('session', {})
    
    # Загружаем или создаем сессию игрока
    user_session = get_session(user_id)
    if not user_session:
        user_session = create_session(user_id)
    
    # Восстанавливаем состояние из session_data
    if 'scene' in session_data:
        user_session.current_scene = session_data.get('scene', 'tavern')
        user_session.step = session_data.get('step', 0)
        user_session.combat_active = session_data.get('combat_active', False)
    
    # Получаем команду от пользователя
    command = req.get('request', {}).get('command', '').lower()
    payload = req.get('request', {}).get('payload', {})
    
    # Определяем действие
    action = payload.get('action', '')
    if not action and command:
        # Простой парсинг команды
        if 'крылышк' in command or 'согласен' in command:
            action = 'agree_wings'
        elif 'осмотр' in command or 'бар' in command:
            action = 'search_bar'
        elif 'напасть' in command or 'атака' in command:
            action = 'attack_bartender'
        elif 'дерев' in command:
            action = 'approach_tree'
        elif 'паук' in command:
            action = 'fight_spiders'
        else:
            action = 'continue'
    
    # Обработка боя, если он активен
    if user_session.combat_active and action in ['attack', 'flee']:
        response = handle_combat_turn(user_session, action, command)
        if response:
            return jsonify(response)
    
    # Обработка действий вне боя
    if action == 'agree_wings':
        text = """Вы соглашаетесь на острые крылышки. Трактирщик уходит на кухню. 
        Вы слышите странные звуки сверху..."""
        user_session.set_flag("wings_agreed", True)
        return build_alice_response(
            text,
            {"scene": "tavern", "step": 1},
            [
                {"title": "🏠 Подняться наверх", "action": "go_upstairs"},
                {"title": "🔍 Подглядеть за трактирщиком", "action": "spy_bartender"}
            ],
            "tower1.png"
        )
    
    elif action == 'spy_bartender':
        text = """Вы подглядываете за Весельчаком и понимаете, что он не готовит крылышки сам, 
        а просто разогревает уже готовые продукты. Что-то здесь не так!"""
        return build_alice_response(
            text,
            {"scene": "tavern", "step": 2},
            [
                {"title": "🏠 Подняться наверх", "action": "go_upstairs"},
                {"title": "🔍 Обыскать бар", "action": "search_bar"}
            ],
            "tower1.png"
        )
    
    elif action == 'search_bar':
        text = """При обыске в баре вы находите вырезанные сообщения: 
        «Путь скрыт за деревом» и «Зло веселится, пока добро спит».
        Также вы видите объявление о пропаже кошки и табличку «Авантюристы месяца». 
        Над объявлением приколот символ культа дракона."""
        user_session.set_flag("bar_searched", True)
        return build_alice_response(
            text,
            {"scene": "tavern", "step": 3},
            [
                {"title": "🏠 Подняться наверх", "action": "go_upstairs"},
                {"title": "🚪 Выйти на улицу", "action": "go_outside"}
            ],
            "tower1.png"
        )
    
    elif action == 'go_upstairs':
        text = """Вы поднимаетесь наверх. В спальне вы видите кровать, закрытый сундук и три картины на стенах.
        Вдруг кровать и сундук начинают шевелиться! Это мимики!"""
        user_session.combat_active = True
        user_session.current_enemy = ENEMIES["mimic"]
        return build_alice_response(
            text + "\n\nНа вас нападает МИМИК! Что будете делать?",
            {"scene": "tavern", "combat_active": True, "step": 4},
            [
                {"title": "⚔️ Атаковать", "action": "attack"},
                {"title": "🍗 Покормить крылышками", "action": "feed_mimic"},
                {"title": "🏃 Сбежать", "action": "flee"}
            ],
            "tower1.png"
        )
    
    elif action == 'go_outside':
        user_session.current_scene = "meadow"
        return jsonify(build_alice_response(
            get_tavern_scene(user_session)["text"],
            {"scene": "meadow", "step": 0},
            [{"title": "🌳 Подойти к дереву", "action": "approach_tree"}],
            "tower1.png"
        ))
    
    elif action == 'approach_tree':
        text = """Вы подходите к огромному дереву. Внезапно ветви начинают шевелиться,
        и на стволе проступает улыбающееся лицо. Пробуждённое дерево говорит:
        «Чародей в башне... он запер дверь в подземелье. Сдвинь камень у моих корней...»"""
        user_session.set_flag("tree_talked", True)
        return build_alice_response(
            text,
            {"scene": "meadow", "step": 1},
            [
                {"title": "🗝️ Сдвинуть камень", "action": "move_rock"},
                {"title": "⬆️ Вернуться в таверну", "action": "back_to_tavern"}
            ],
            "tower1.png"
        )
    
    elif action == 'move_rock':
        text = """Вы сдвигаете камень и находите дверь в подземелье. 
        Дверь заперта магическим замком. Нужен золотой ключ."""
        return build_alice_response(
            text,
            {"scene": "meadow", "step": 2},
            [
                {"title": "🔍 Искать ключ у пауков", "action": "fight_spiders"},
                {"title": "⬆️ Вернуться в таверну", "action": "back_to_tavern"}
            ],
            "tower1.png"
        )
    
    elif action == 'fight_spiders':
        user_session.combat_active = True
        user_session.current_enemy = ENEMIES["giant_spider"]
        return build_alice_response(
            "На вас нападает гигантский паук!",
            {"scene": "meadow", "combat_active": True, "step": 3},
            [
                {"title": "⚔️ Атаковать", "action": "attack"},
                {"title": "🏃 Сбежать", "action": "flee"}
            ],
            "tower1.png"
        )
    
    elif action == 'continue':
        # Переход к следующей сцене
        if user_session.current_scene == "meadow":
            user_session.current_scene = "dungeon"
            return jsonify(build_alice_response(
                "Вы спускаетесь в подземелье...",
                {"scene": "dungeon", "step": 0},
                [{"title": "🔍 Осмотреться", "action": "continue"}],
                "tower1.png"
            ))
        elif user_session.current_scene == "dungeon":
            # Переход к финалу
            user_session.current_scene = "dragon"
            return jsonify(build_alice_response(
                "Вы достигаете вершины башни. Перед вами стоит Эрван Душегуб с драконьим яйцом!",
                {"scene": "dragon", "step": 0},
                [
                    {"title": "⚔️ Сразиться с Эрваном", "action": "fight_ervan"},
                    {"title": "🐉 Призвать дракона", "action": "summon_dragon"}
                ],
                "evil2.png"
            ))
    
    elif action == 'fight_ervan':
        user_session.combat_active = True
        user_session.current_enemy = ENEMIES["ervan_wizard"]
        return build_alice_response(
            "Эрван Душегуб готовится к бою!",
            {"scene": "dragon", "combat_active": True, "step": 1},
            [
                {"title": "⚔️ Атаковать", "action": "attack"},
                {"title": "🏃 Сбежать", "action": "flee"}
            ],
            "evil2.png"
        )
    
    elif action == 'summon_dragon':
        return build_alice_response(
            "Вы используете Око Дракона! Небо темнеет, и прилетает Пеплорёв — красная дракониха!",
            {"scene": "dragon", "step": 2},
            [
                {"title": "⚔️ Сражаться с драконом", "action": "fight_dragon"},
                {"title": "🎭 Натравить дракона на Эрвана", "action": "pit_them"}
            ],
            "dragon.png"
        )
    
    elif action == 'fight_dragon':
        user_session.combat_active = True
        user_session.current_enemy = ENEMIES["dragon"]
        return build_alice_response(
            "Пеплорёв атакует вас огненным дыханием!",
            {"scene": "dragon", "combat_active": True, "step": 3},
            [
                {"title": "⚔️ Атаковать", "action": "attack"},
                {"title": "🏃 Сбежать", "action": "flee"}
            ],
            "dragon.png"
        )
    
    elif action == 'pit_them':
        text = """Вы выкрикиваете: «Это он украл твоё яйцо!». Пеплорёв переключает внимание на Эрвана.
        Пока они сражаются, вы хватаете яйцо и убегаете!"""
        return build_alice_response(
            text + "\n\n🎉 ПОЗДРАВЛЯЮ! Вы завершили приключение!",
            {"scene": "victory"},
            [{"title": "Начать заново", "action": "restart"}],
            "hero1.png",
            end_session=True
        )
    
    elif action == 'restart':
        new_session = create_session(user_id)
        return jsonify(build_alice_response(
            "Приключение начинается заново!",
            {"scene": "tavern", "step": 0},
            [{"title": "🍗 Согласиться на крылышки", "action": "agree_wings"}],
            "hero1.png"
        ))
    
    # Действие по умолчанию
    scene_name = user_session.current_scene
    scene_func = SCENES.get(scene_name, get_tavern_scene)
    scene_data = scene_func(user_session)
    
    return jsonify(build_alice_response(
        scene_data["text"],
        {"scene": scene_name, "step": user_session.step, "combat_active": user_session.combat_active},
        scene_data.get("buttons", []),
        scene_data.get("image", "hero1.png")
    ))

@app.route('/')
def index():
    """Веб-интерфейс для тестирования"""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
