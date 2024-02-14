import random
import time
from collections import defaultdict
from sadlib.sadqueue import push, pull, subscribe

arrived_messages_dict = defaultdict(list)


def f1(key, msg):
    print("F1 received a message", msg)
    global arrived_messages_dict
    arrived_messages_dict['f1'].append(msg)


def f2(key, msg):
    print("F2 received a message", msg)
    global arrived_messages_dict
    arrived_messages_dict['f2'].append(msg)


def f3(key, msg):
    print("F3 received a message", msg)
    global arrived_messages_dict
    arrived_messages_dict['f3'].append(msg)


def simple_print(key, msg):
    print(f"a message arrived in simple_print: {msg}")


def test_push_pull():
    print("Start pushing messages to server.")
    messages_length = int(input("how many messages to test="))

    counter = 1
    while counter <= messages_length:
        try:
            message = f"message-{counter}"
            print(f"pushing {message}")
            push(message, message)
            counter += 1
        except Exception as e:
            print(f"Error: {e}")
            break
    print("Pushing completed. lets start pulling messages")
    time.sleep(5)
    counter = 1
    while counter <= messages_length:
        try:
            message = f"message-{counter}"
            print(f"pulling to see: {message}")
            _, response = pull()
            assert response == message
            print("correct!")
            counter += 1
        except Exception as e:
            print(f"ERROR: {e}")
            break


def test_subscribe():
    print("start subscribing with different functions...")
    subscribe(f1)
    subscribe(f2)
    subscribe(f3)

    print("subscription completed. start pushing several messages...")
    messages_length = int(input("how many messages to test="))

    for msg in range(1, messages_length + 1):
        push(f"sbs-{msg}", f"sbs-{msg}")
    time.sleep(5)

    print("pushing completed. start checking if subscriptions worked...")
    global arrived_messages_dict
    arrived_messages_set = set()

    counter = 0
    for func, msg_list in arrived_messages_dict.items():
        counter += len(msg_list)
        for msg in msg_list:
            arrived_messages_set.add(msg)

    print("check if all messages arrived...")
    assert counter >= messages_length
    print("DONE!\ncheck for duplication...")
    assert counter == len(arrived_messages_set)
    print("DONE!")


while True:
    opt = input("1. test push/pull\n2. test subscribe\n3. manual push\n4. manual pull\n5. manual subscribe\n")
    if opt == "1":
        test_push_pull()
    if opt == "2":
        test_subscribe()
    if opt == "3":
        try:
            push(input("key="), input("value="))
        except Exception:
            print("key already exists")
    if opt == "4":
        try:
            print(pull())
        except Exception:
            print("no message to pull")
    if opt == "5":
        subscribe(simple_print)
