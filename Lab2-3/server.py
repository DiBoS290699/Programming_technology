import socket
import saver
from definitions import *

# list of Card
table = []

cards = [dict(), dict()]

cur_cl_id = 0

msg_s = Msg_server()
msg_c = Msg_client()


def table_info():
    cards_on_table = {1: 0, 2: 0, 3: 0}
    for card in table:
        cards_on_table[card["real"]] += 1
    return cards_on_table


def start_new_game():
    global cur_cl_id
    table.clear()
    cards[0].clear()
    cards[0].update(DEFAULT_CARDS)
    cards[1].clear()
    cards[1].update(DEFAULT_CARDS)
    cur_cl_id = 0


def launch_game(s, clients):
    global cur_cl_id, table, cards

    load = False
    user_0 = False
    user_1 = False
    while not (user_0 and user_1):
        data, addr = s.recvfrom(1024)
        if addr != clients[0] and addr != clients[1]:
            s.sendto(send_msg(msg_s.SERVER_FULL), addr)
        else:
            if addr == clients[0]:
                user_0 = True
            if addr == clients[1]:
                user_1 = True
            msg, _, _ = recv_msg(data)
            if msg == msg_c.LOAD_GAME:
                load = True
            else:
                load = False

    if load:
        data = saver.load_game_state_from_json(JSON_FILE_PATH)
        if data is None:
            load = False
        elif data.__class__ == "".__class__:
            print(data)
            load = False
        else:
            table = data[0]
            cards = data[1]
            cur_cl_id = data[2]
            s.sendto(send_msg(msg_s.GET_CARDS, KEY_CARDS, cards[0]), clients[0])
            s.sendto(send_msg(msg_s.GET_CARDS, KEY_CARDS, cards[1]), clients[1])
            print("-------------Launch a saved game-------------")
            s.sendto(send_msg(msg_s.MOVE_1, KEY_MESSAGE_ADD, "Game begins, table is empty"), clients[cur_cl_id])
    if not load:
        start_new_game()
        s.sendto(send_msg(msg_s.GET_CARDS, KEY_CARDS, cards[0]), clients[0])
        s.sendto(send_msg(msg_s.GET_CARDS, KEY_CARDS, cards[0]), clients[1])
        print("-------------Start the new game, table is empty-------------")

        s.sendto(send_msg(msg_s.MOVE_1, KEY_MESSAGE_ADD,
                          "-------------Start the new game, table is empty-------------"), clients[0])


    game_end = False

    while True:

        data, addr = s.recvfrom(1024)
        if addr != clients[0] and addr != clients[1]:
            s.sendto(send_msg(msg_s.SERVER_FULL), addr)

        elif addr != clients[cur_cl_id]:
            s.sendto(send_msg(msg_s.WRONG_ATTEMPT), addr)

        else:

            msg, key, recv_data = recv_msg(data)
            if msg == msg_c.BELIEVE:
                secret_card = recv_data
                table.append(secret_card)
                cards[cur_cl_id][str(secret_card["real"])] -= 1
                fake_number = secret_card["fake"]
                info = f"Player #{cur_cl_id} put the card and named it {fake_number}\n" \
                       f"Number of cards on the table: {len(table)}"
                s.sendto(send_msg(msg_s.MOVE_N, KEY_MESSAGE_ADD, info), clients[1 - cur_cl_id])

            elif msg == msg_c.NOT_BELIEVE:
                cards_on_table = table_info()

                if table[-1]["real"] == table[-1]["fake"]:
                    s.sendto(send_msg(msg_s.FAIL_YOU_WRONG, KEY_CARDS, cards_on_table), clients[cur_cl_id])
                    update_cards(cards[cur_cl_id], cards_on_table)
                    table.clear()
                    info = "Your opponent didn't believe you and made a mistake. He took the cards from the table. " \
                           "Do the move"
                    s.sendto(send_msg(msg_s.MOVE_1, KEY_MESSAGE_ADD, info), clients[1 - cur_cl_id])

                else:
                    s.sendto(send_msg(msg_s.GOOD_YOU_RIGHT), clients[cur_cl_id])
                    s.sendto(send_msg(msg_s.FAIL_OTHER_RIGHT, KEY_CARDS, cards_on_table), clients[1 - cur_cl_id])
                    update_cards(cards[1 - cur_cl_id], cards_on_table)
                    table.clear()

            elif msg == msg_c.BELIEVE_WIN:
                s.sendto(send_msg(msg_s.YOU_WIN), clients[cur_cl_id])
                s.sendto(send_msg(msg_s.YOU_LOSE), clients[1 - cur_cl_id])
                game_end = True
                break

            elif msg == msg_c.EXIT:
                s.sendto(send_msg(msg_s.CLIENT_EXIT), clients[1 - cur_cl_id])
                break

            else:
                pass

            cur_cl_id = 1 - cur_cl_id

    if not game_end:
        saver.save_game_state_to_json(table, cards, cur_cl_id, JSON_FILE_PATH)
        print("The Game has saved")
        pass


def main():
    s = None
    try:
        host = socket.gethostbyname(socket.gethostname())
        port = PORT
        clients = []
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((host, port))

        print("[ Server Started ]")
        print(f"The host name: {socket.gethostname()}")
        print("Waiting for players")

        while True:

            data, addr = s.recvfrom(1024)

            if addr in clients:
                msg, _, _ = recv_msg(data)
                if msg == msg_c.EXIT:
                    clients.remove(addr)

            elif addr not in clients:
                # new client
                clients.append(addr)
                if len(clients) == 1:
                    s.sendto(send_msg(msg_s.GREETING, KEY_MESSAGE_ADD, '0'), addr)
                    print("Player №0 connected")
                if len(clients) == 2:
                    s.sendto(send_msg(msg_s.GREETING, KEY_MESSAGE_ADD, '1'), addr)
                    print("Player №1 connected")

            if len(clients) == 2:
                launch_game(s, clients)
                s.close()
                return

    except Exception as e:
        print(e)
        print("\n[ Server Stopped ]")
        s.close()
        return


if __name__ == "__main__":
    main()
