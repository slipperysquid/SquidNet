import threading,time, server, socket, errno

class Session(threading.Thread):

    def __init__(self,connection=None, ID = 0):
        '''
            Takes connection (default None)
            Takes ID (default 0)
        '''
        self.connection = connection
        self.id = ID
        self.create_time = time.time()
        
        self.abort = False

    def kill(self):
        "close the session and restart interaction with the command and CONTROL"
        #TODO: dont know if we will have time to implement tcp shell so this might not be needed
        self._active.clear()
        globals()['CommandServer'].current_session = None
        
    
    def check_connection(self, timeout=2):
        """Debugging function to check connection between sockets with a timeout.

            Args:
                timeout: The maximum time to wait for a response in seconds.

            Returns:
                True if the connection is successful within the timeout, False otherwise.
        """
        
        self.connection.setblocking(0)
        
        start = time.time()
        
        try:
            self.connection.send('g'.encode())
            while True:
                try:
                    response = self.connection.recv(1)
                    if str(response.decode()) == 'g':
                        return True
                    else:
                        return False
                except socket.error as e:
                    if e.errno == errno.EWOULDBLOCK or e.errno == errno.EAGAIN:
                        #no data received
                        if time.time() - start >= timeout:
                            return False
                        else:
                            time.sleep(0.1)
                    else:
                        raise e
        except Exception as e:
            print(f"check_connection: {e}")
            return False        
        finally:
            self.connection.setblocking(1)
    #sends task to victim
    def send_instruction(self):
        #TODO:implement
        return

    #receives output from task running on victim
    def receive_response(self):
        #TODO:implement
        return
    '''
    #Reverse TCP shell
    def run(self):
        while True:
            if self.active.wait():
                #TODO:implement reverse TCP shell need to make the run() function in server threaded first so that this can run instead when active
                #Also maybe move some command handling in here instead of server.run() or maybe both? not sure if thats useful or not
                pass
            else:
                if self.abort():
                    break

        self.active.clear()
        '''