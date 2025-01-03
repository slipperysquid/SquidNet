import socket,threading,helpers



class client():

    def __init__(self, host, port):
        self.host = host
        self.host_port = port
        self.connection = self.connect()

    #TODO: constantly listen for a connection and perform a task based on the message received 
    def connect(self):
        print("creating connection")
        connection = socket.create_connection((self.host,self.host_port))
        data = connection.recv(1)
        if str(data.decode()) == 'g':
            print("connection established")
            connection.send('g'.encode())
        
        return connection
    
    def run(self):
        while True:
            data = self.connection.recv(1024)
            if not data:
                break
            print(data.decode())
        return
            
            
c = client('localhost', 5000)
print("hello world")
   