from aiogram.fsm.state import State, StatesGroup

class Questionnaire(StatesGroup):
    """
    FSM состояния для процесса заполнения анкеты в Roblox-хаус.
    """
    name = State()     # Шаг 1: Имя
    age = State()      # Шаг 2: Возраст
    country = State()  # Шаг 3: Страна
    photo = State()    # Шаг 4: Скриншот скина Roblox
    confirm = State()  # Подтверждение данных перед отправкой
