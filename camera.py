import socket, base64,cv2



#TODO:take picture
camera = cv2.VideoCapture(0)
return_value, pic = camera.read()

#TODO:encode picture
encoded = base64.b64encode(cv2.imencode('.png',pic)[1].tobytes())
#TODO:send picture to server
sock = socket.create_connection(('localhost',5000))
sock.send(encoded)


