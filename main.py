import requests
import uuid
import threading
import websocket
import urllib.parse

# TODO: use correct host path according to the server and environment
hosts = ["http://host1", "http://host2"]


# TODO: /check endpoint must be defined in server first
def check_host(host):
    try:
        response = requests.get(f"{host}/check")
        return response.status_code == 200
    except requests.ConnectionError:
        return False


def find_living_host():
    for host in hosts:
        if check_host(host):
            return host
    return None


# TODO: check if parameters are passing to server correctly
def push_message(host):
    message = input("Enter a message to push: ")
    key = str(uuid.uuid4())
    params = urllib.parse.urlencode({'key': key, 'value': message})
    response = requests.post(f"{host}/push?{params}")
    if response.status_code == 200:
        print("Message pushed successfully.")
    else:
        print("Failed to push the message.")


def pull_message(host):
    response = requests.get(f"{host}/pull")
    if response.status_code == 200:
        data = response.json()
        print(f"Pulled message: {data['value'].decode()}")
    else:
        print("Failed to pull a message.")


# TODO check if  Websocket is working correctly
def subscribe_to_messages(host, func):
    def on_message(ws, message):
        func(message)

    def on_error(ws, error):
        print(f"WebSocket error: {error}")

    def on_close(ws, close_status_code, close_msg):
        print("WebSocket closed")

    def on_open(ws):
        print("WebSocket connection opened.")

    ws_url = host.replace("http", "ws") + "/subscribe"
    ws = websocket.WebSocketApp(ws_url,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    thread = threading.Thread(target=lambda: ws.run_forever(), daemon=True)
    thread.start()


# TODO: how to set a function on subscribed messages?
def on_message_received(message):
    print(f"New message received: {message}")


# TODO: check if we need a GUI
def run_client():
    host = find_living_host()
    if host:
        print(f"Connected to {host}.")
        while True:
            action = input("Choose an action (push, pull, subscribe or exit): ").lower()
            if action == "push":
                push_message(host)
            elif action == "pull":
                pull_message(host)
            elif action == "subscribe":
                subscribe_to_messages(host, on_message_received)
                print("Subscribed to messages. Listening...")
            elif action == "exit":
                print("Exiting...")
                break
            else:
                print("Invalid action. Please try again.")
    else:
        print("No available hosts found.")


if __name__ == "__main__":
    run_client()
