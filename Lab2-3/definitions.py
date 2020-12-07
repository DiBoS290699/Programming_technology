import json


class Msg_client:
    def __init__(self):
        self.JOINED = "joined"
        self.EXIT = "exit"
        self.BELIEVE = "believe"
        self.BELIEVE_WIN = "believe_win"
        self.NOT_BELIEVE = "not_believe"
        self.NEW_GAME = "Start the new game"
        self.LOAD_GAME = "Load game"

# ---------------------------------------------

class Msg_server:
    def __init__(self):
        self.GREETING = "You're player #"
        self.GET_CARDS = "Get your cards."
        self.MOVE_1 = "Do the first move."
        self.MOVE_N = "Do the move."
        self.SERVER_FULL = "Server is full."
        self.WRONG_ATTEMPT = "This is not your move."
        self.FAIL_YOU_WRONG = "You didn't believe it and you were WRONG. Get all the cards on table."
        self.FAIL_OTHER_RIGHT = "The opponent didn't believe it and was right. Get all the cards on table."
        self.GOOD_YOU_RIGHT = "You didn't believe it and you were RIGHT"
        self.YOU_LOSE = "You lose"
        self.YOU_WIN = "You win"
        self.CLIENT_EXIT = "Your opponent is out of the game. The game will be saved"


JSON_FILE_PATH = "save.json"
WRONG_TRANSMISSION = "Transmission format error"
KEY_SECRET_CARD = 'secret_card'
KEY_CARDS = 'cards'
KEY_MESSAGE_ADD = 'msg_add'

DEFAULT_CARDS = {1: 3, 2: 2, 3: 1}

PORT = 8080
SERVER = ("DESKTOP-QIE30SR", PORT)


def send_msg(msg, key=None, send_data=None):
    d = {"message": msg,
         key: send_data}
    return json.dumps(d).encode("utf-8")


def recv_msg(data):
    d = json.loads(data.decode("utf-8"))
    key = list(d.keys())[1]
    if key == KEY_SECRET_CARD:
        for i in d[key].keys():
            d[key][i] = int(d[key][i])
    return d["message"], key, d[key]


def update_cards(destination: dict, cards_to_dump: dict):
    keys = cards_to_dump.keys()
    for key in keys:
        if key not in destination.keys():
            destination.update({key: 0})
        destination[key] += cards_to_dump[key]
