import socket,threading,helpers


def main():
    c = client('localhost', 5000)
    return


class client():

    def __init__(self, host, port):
        self.host = host
        self.host_port = port
        self.connection = self.connect()

    #TODO: constantly listen for a connection and perform a task based on the message received 
    def connect(self):
        connection = socket.create_connection((self.host,self.host_port))
        data = connection.recv(1)
        if str(data.decode() == 'g'):
            print("connection established")

main()