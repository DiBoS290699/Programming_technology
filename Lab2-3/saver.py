import json
import jsonschema
from jsonschema import validate
from definitions import *

# взаимодействие с джейсоном
schema = {
    "type": "object",
    "required": [
        "table",
        "cards",
        "cur_cl_id"
    ],
    "properties": {
        "table": {
            "type": "array",
            "items": [
                {
                    "type": "object",
                    "required": [
                        "real",
                        "fake"
                    ],
                    "properties": {
                        "real": {"type": "integer"},
                        "fake": {"type": "integer"}
                    },
                    "additionalProperties": True
                }
            ]
        },
        "cards": {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "items": [
                {
                    "type": "object",
                    "required": [
                        "1",
                        "2",
                        "3"
                    ],
                    "properties": {
                        "1": {"type": "integer"},
                        "2": {"type": "integer"},
                        "3": {"type": "integer"}
                    },
                    "additionalProperties": True
                }
            ]
        },
        "cur_cl_id": {
            "type": "integer"
        }
    },
    "additionalProperties": True
}


def parsing(data):
    print("hey")
    table = []
    data_copy = data['table']
    print(data_copy)
    for elem in data_copy:
        elem['real'] = int(elem['real'])
        elem['fake'] = int(elem['fake'])
        print(elem)
        table.append(elem)
    cards = []
    data_copy = data['cards']
    print(data_copy)
    for player in data_copy:
        for key in player.keys():
            player[key] = int(player[key])
        cards.append(player)
    cur_cl_id = data["cur_cl_id"]
    return table, cards, cur_cl_id

         
def validate_json(data):
    try:
        validate(instance=data, schema=schema)
    except jsonschema.exceptions.ValidationError:
        return False
    return True


def load_game_state_from_json(json_file_path):
    with open(json_file_path) as json_file:
        try:
            data = json.load(json_file)
            if validate_json(data):
                return list(parsing(data))
            else:
                raise json.decoder.JSONDecodeError
        except json.decoder.JSONDecodeError:
            return "You don`t have actually saved game. Start the new game."
    return None


def save_game_state_to_json(table, cards, cur_cl_id, json_file_path):
    data = {
        "table": table,
        "cards": cards,
        "cur_cl_id": cur_cl_id
    }
    with open(json_file_path, 'w') as file:
        json.dump(data, file, indent=4)

