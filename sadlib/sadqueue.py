import json
import random

import requests
import uuid
import threading
import websocket
import urllib.parse
from sadlib import HOSTS

live_host = HOSTS[0]


def check_host(host):
    try:
        response = requests.get(f"{host}/-/ready", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def find_live_host():
    for host in HOSTS:
        if check_host(host): return host
    return None


def get_live_host():
    random.shuffle(HOSTS)
    return find_live_host()


def push(message):
    host = get_live_host()
    if host is None:
        raise Exception("No available sadqueue host found")

    key = str(uuid.uuid4())
    params = urllib.parse.urlencode({'key': key, 'value': message})
    response = requests.post(f"{host}/push?{params}")
    if response.status_code != 200:
        raise Exception("Failed to push the message.")


def pull():
    host = get_live_host()
    if host is None:
        raise Exception("No available sadqueue host found")

    response = requests.get(f"{host}/pull")
    if response.status_code == 200:
        data = response.json()
        return data['value']

    raise Exception("Failed to pull from sadqueue server")


def subscribe(func):
    host = get_live_host()
    if host is None:
        raise Exception("No available sadqueue host found")

    def on_message(ws, message):
        if message == "You subscribe successfully":
            pass
        else:
            func(message)

    def on_open(ws):
        ws.send("subscribe\n")  # Send initial message upon opening the connection

    ws_url = host.replace("http", "ws") + "/subscribe"
    ws = websocket.WebSocketApp(ws_url, on_message=on_message, on_open=on_open)
    thread = threading.Thread(target=lambda: ws.run_forever(), daemon=True)
    thread.start()
