from enum import Enum, auto
import random
import requests as req

SERVER_URL = "http://51.250.28.5:8000/"
# SERVER_URL = "http://localhost:8000/"


class State(Enum):
    pairing = auto()
    paired = auto()
    unknown = auto()
    wrongPass = auto()


AliceId = str
# assume that this is redis database hehe


def handler(event, context):
    print(event)

    text = "Привет, я Алафа! Ваш финансовый ассистент"
    aliceId = event["session"]["user"]["user_id"]
    userId = select_user_id(aliceId)
    command = event["request"]["command"]

    answer: str

    session_state = event.get("state", {}).get("user", {})
    state = State.__members__.get(session_state.get("state", "unknown"))
    print(state)
    print(session_state)

    if state == State.pairing:
        original_text = "".join(event["request"]["nlu"]["tokens"])
        answer, state = do_pairing(aliceId, original_text)
    elif state == State.wrongPass:
        if command in ["да", "конечо", "ещё раз"]:
            state = State.pairing
            answer = "Хорошо, назовите код, пожалуйста"
        elif command in ["нет", "не надо", "хватит"]:
            state = State.unknown
            answer = "Хорошо, если что, скажите дружба"
        else:
            answer = "Кажется не понял, если что, скажите дружба"
            state = State.unknown
    elif command in ["баланс", "деньги", "узнать баланс"]:
        answer = handle_balance(userId, state)
    elif command in [
        "коннект",
        "пара",
        "спариться",
        "соединить",
        "войти",
        "знакомство",
        "сконнектится",
        "дружба",
    ]:
        state = State.pairing
        answer = start_pairing()
    elif state == State.paired:
        if command in ["спасибо", "благодарю", "благодарен", "благодарна"]:
            answer = "Всегда рад помочь"
        if command in ["прощаюсь", "выход", "пока"]:
            answer = "Рад был поболтать) Увидимся"
            state = State.unknown
        elif any(map(lambda x: x in command, ["совет", "посоветуй", "посоветуешь"])):
            answer = random_advice()
        else:
            answer = random.choice(
                [
                    'Скажите "баланс", и я его подскажу)',
                    "Могу дать совет. Чего изволите?",
                    "Чем могу помочь?",
                    "Изволите чего?",
                ]
            )
    elif state == State.unknown:
        answer = 'Привет, я алафа, ваш финансовый ассистент! Скажите "дружба" и я начну помогать вам'
    else:
        answer = (
            f"Вы можете попросить меня подружиться. Я буду стараться помочь вам, обещаю"
        )

    session_state["state"] = state.name
    return {
        "version": event["version"],
        "session": event["session"],
        "response": {
            "text": answer,
            "end_session": "false",
        },
        "user_state_update": session_state,
    }


def random_advice() -> str:
    return random.choice(
        [
            "Если вы не победите себя, тогда будете побеждены самим собой.",
            "Многие люди никогда не сделают прорыв в своей жизни, потому что они отказались выйти из зоны комфорта и сделать шаг в неизвестность…!",
            "Успеха добивается лишь тот, кто остается после того как все остальные уходят.",
            "Успешный человек больше сосредоточен на том, чтобы делать правильные вещи вместо того, чтобы делать вещи правильно.",
            "Чем просто хотеть рыбы, лучше начни плести сети, чтобы её поймать.",
            "Если ты не можешь, тогда должен. А если должен, значит сможешь.",
        ]
    )


def handle_balance(userId, state: State):
    if state != State.paired:
        return "Простите, но нужно познакомиться чтобы я мог вам подсказать"

    balances = get_balances(userId)
    return (
        "Хорошо. Ваши активы:"
        + ", ".join(
            map(
                lambda x: f'Счет. {x["name"]}, баланс {x["balance"]} {x["currency"]}',
                balances,
            )
        )
        + "."
    )


def select_user_id(aliceId):
    r = req.post(SERVER_URL + "select_user_id", json={"alice_id": aliceId})
    return r.json().get("user_id", None)


def get_balances(userId):
    r = req.post(SERVER_URL + "balances", json={"user_id": userId})
    return r.json().get("data", [])


def start_pairing():
    return "Произнесите код с мобильного приложения. Там несколько цифр"


def do_pairing(aliceId, code):
    r = req.post(SERVER_URL + "pair_alice", json={"alice_id": aliceId, "code": code})
    print(r.json())
    result = r.json().get("user_id", None)
    if result == None:
        return ("Хм, кажется код не подошел. Попробуем еще раз?", State.wrongPass)
    return ("Отлично! Рад познакомиться!", State.paired)


if __name__ == "__main__":
    pass
    # print(do_pairing("alice test", "7687"))
    # userId = select_user_id("alice test")
    # print(get_balances("alice test"))
    # print(get_balances(userId))
    # print(handle_balance(userId, State.paired))

    # state = State.__members__.get({}.get("session_state", {}).get("state", "unknown"))
    # print(state)
