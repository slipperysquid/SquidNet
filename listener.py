import socket,time,base64


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost',5000))
server_socket.listen()

buffer = 10000000
print('listening on port 5000...')
while True:
    time.sleep(1)
    victim,ip = server_socket.accept()
    data = victim.recv(buffer)
    if data.lower() == 'q':
        server_socket.close()
        break
    if data:
        if data.lower() == 'q':
            server_socket.close()
            print('quitting')
            break
        else:
            print('RECEIVED IMAGE')
            image = open('image.png','wb')
            image.write(base64.b64decode(data))
            image.close()
            
        