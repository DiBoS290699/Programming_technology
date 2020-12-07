import threading
import socket
import json
from definitions import *

host = socket.gethostbyname(socket.gethostname())  # получаем ip хоста
port = 0
server = SERVER

cards = {}

msg_c = Msg_client()
msg_s = Msg_server()

def input_int(prompt):
    while True:
        s = input(prompt)
        if s.lower() == "exit":
            return None
        elif s != '1' and s != '2' and s != '3':
            print("Integer value required")
        else:
            return s


def print_cards():
    print("---------------------Your cards:", end='\t')
    for key in cards.keys():
        if cards[key] != 0:
            print(f"{cards[key]} '{key}'-s;\t", end='')
    print()


def cards_count():
    return sum(cards.values())


def input_YN(prompt):
    s = input(prompt).lower()
    if s == "exit":
        return None
    while s not in ['y', 'n']:
        s = input(prompt).lower()
        if s == "exit":
            return None
    return s == 'y'


def drop_secret_card():
    available_nominals = cards.keys()

    real = input_int("Input card's nominal you want to drop: ")
    if real is None:
        return None
    real = str(real)
    while (real not in available_nominals) or cards[real] == 0:
        print("You actually don't have this card")
        real = input_int("Input card's nominal you want to drop: ")
        if real is None:
            return None

    available_fake_nominals = available_nominals  # [1, 2, 3]
    fake = input_int(f"Input it's fake nominal ({available_fake_nominals}): ")
    if fake is None:
        return None
    while fake not in available_fake_nominals:
        print(f"You must say the number from {available_fake_nominals}")
        fake = input_int(f"Input it's fake nominal ({available_fake_nominals}): ")
        if fake is None:
            return None

    cards[real] -= 1
    print(f"You dropped a '{real}' and said it's '{fake}'")
    print_cards()

    return {"real": real, "fake": fake}


def run(s):
    # receive cards
    load_game = input_YN("Load a saved game? (y/n): ")
    if load_game is None:
        s.sendto(send_msg(msg_c.EXIT), server)
        return
    elif load_game:
        s.sendto(send_msg(msg_c.LOAD_GAME), server)
    else:
        s.sendto(send_msg(msg_c.NEW_GAME), server)
    data, addr = s.recvfrom(1024)

    msg, key, recv_data = recv_msg(data)
    if msg != msg_s.GET_CARDS or key != KEY_CARDS:
        print(WRONG_TRANSMISSION)
        s.close()
        return

    cards.clear()
    cards.update(recv_data)
    print_cards()

    while True:
        # receive cards
        data, addr = s.recvfrom(1024)

        msg, key, recv_data = recv_msg(data)

        if msg == msg_s.MOVE_1:  # !
            print(msg)
            print(recv_data)
            secret_card = drop_secret_card()
            if secret_card is None:
                s.sendto(send_msg(msg_c.EXIT), server)
                break
            else:
                s.sendto(send_msg(msg_c.BELIEVE_WIN if cards_count() == 0 else msg_c.BELIEVE,
                                  KEY_SECRET_CARD, secret_card), server)
            print("Move is done. Your opponent's move.")

        elif msg == msg_s.MOVE_N:  # !
            print(msg)
            print(recv_data)
            YN = input_YN("Do you believe? (y/n): ")
            if YN is None:
                s.sendto(send_msg(msg_c.EXIT), server)
                break
            elif YN:
                secret_card = drop_secret_card()
                if secret_card is None:
                    s.sendto(send_msg(msg_c.EXIT), server)
                    break
                else:
                    s.sendto(send_msg(msg_c.BELIEVE_WIN if cards_count() == 0 else msg_c.BELIEVE,
                                      KEY_SECRET_CARD, secret_card), server)
                print("Move is done. Your opponent's move.")
            else:
                s.sendto(send_msg(msg_c.NOT_BELIEVE), server)
                print("You don't believe. Waiting for response...")

        elif msg == msg_s.FAIL_OTHER_RIGHT:  # !
            print(msg)
            update_cards(cards, recv_data)
            print_cards()
            # empty table, so doing firs move
            print("Your move. Table is empty")
            secret_card = drop_secret_card()
            if secret_card is None:
                s.sendto(send_msg(msg_c.EXIT), server)
                break
            else:
                s.sendto(send_msg(msg_c.BELIEVE_WIN if cards_count() == 0 else msg_c.BELIEVE,
                                  KEY_SECRET_CARD, secret_card), server)
            print("Move is done. Your opponent's move.")

        elif msg == msg_s.FAIL_YOU_WRONG:
            print(msg)
            update_cards(cards, recv_data)
            print_cards()
            print("Move is done. Your opponent's move.")

        elif msg == msg_s.GOOD_YOU_RIGHT:
            print(msg)
            print("Move is done. Your opponent's move.")

        elif msg == msg_s.YOU_LOSE or msg == msg_s.YOU_WIN or msg == msg_s.CLIENT_EXIT:
            print(msg)
            break

        elif msg_s.WRONG_ATTEMPT:
            print(msg)

        else:
            pass


def main():
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((host, port))
    except (socket.error, OverflowError) as e:
        print("Неполадки с сервером 1")
        print(e)
        s.close()
        return

    s.setblocking(True)

    try:
        s.sendto(send_msg(msg_c.JOINED), server)
        data, addr = s.recvfrom(1024)
    except (ConnectionAbortedError,
            ConnectionResetError) as e:
        print("неполадки с сервером 2")
        print(e)
        s.close()
        return

    msg, _, recv_data = recv_msg(data)
    if msg == msg_s.SERVER_FULL:
        print(msg)
        s.close()
        return

    if msg == msg_s.GREETING:
        print(msg + recv_data)

    # run(s)
    threading.Thread(target=run, args=(s,)).start()


if __name__ == "__main__":
    main()
