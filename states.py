from aiogram.fsm.state import State, StatesGroup

class Questionnaire(StatesGroup):
    """
    FSM состояния для процесса заполнения анкеты в Roblox-хаус.
    """
    name = State()              # Шаг 1: Имя
    age = State()               # Шаг 2: Возраст
    country = State()           # Шаг 3: Страна
    roblox_username = State()   # Шаг 4: Никнейм в Roblox (с авто-проверкой скина и даты через API)
    confirm = State()           # Подтверждение данных перед отправкой
