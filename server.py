


import psutil
import signal
import threading, socket, colorama, helpers,session, socketserver,select, subprocess, os
import random




class server():
    #TODO: implement what a "instruction" payload to send to the client is, (maybe json?, dictionarty?)
    def __init__(self, host='localhost', port = 5000, db='memory'):
        self.socket = self._socket(port)
        self.sessions = []
        self.current_session = None
        self.host = host
        self.port = port
        self.db = db
        self.app = None
        self.threads = []
        self.commands = {

            'hello' : {
                'method': self._hello,
                'use' : 'hello',
                'desc' : 'Says hello!'
            },

            'quit' : {
                'method': self._quit,
                'use' : 'quit',
                'desc' : 'Closes the server and stops the program.'
            },

            'commands' : {
                'method': self._commands,
                'use' : 'commands',
                'desc' : 'Lists all commands.'
            },

            'help' : {
                'method' : self._help,
                'use' : 'help <command>',
                'desc' : 'Gives the description and usage of a command.' 
            },
            
            'session' : {
                'method' : self._sesh,
                'use' : 'session <session_id>',
                'desc' : 'Changes the current session to the session with the specified ID.'
            }
        
        }

    def _help(self, command):
        '''list the command and its usage'''
        if (command in self.commands):
            out = """
            Usage: {0}
            Description: {1}
            """.format(self.commands[command]['use'],self.commands[command]['desc'])
        else:
            raise Exception("Unknown command: \"{}\"".format(command))
        return out
        

    @helpers.make_threaded
    def get_client_connection(self):
        '''wait for a client to connect on a different thread and create a new session'''
        while True and not globals()['close']:
            self.socket.settimeout(0.1)
            try:
                connection, ip = self.socket.accept()
                helpers.show("\nRECEIVED CONNECTION REQUEST FROM: {}".format(ip), colour="GREEN", end="\n->")
                session_id = random.randint(1000, 9999)
                new_session = session.Session(connection, session_id)
                if new_session.check_connection():
                    helpers.show("CONNECTION SUCCESSFUL", colour="GREEN", style="BRIGHT", end="\n->")
                    
                    self.sessions.append(new_session)
                    helpers.show("CREATED NEW SESSION WITH ID " + str(session_id), colour="BLUE", style="BRIGHT", end="\n->")
                else:
                    helpers.show("CONNECTION FAILED", colour="RED", style="BRIGHT", end="\n->")
            except socket.timeout:
                pass    

        helpers.show("STOPPING LISTENING SOCKET", colour="RED", style="BRIGHT", end="\n")   
    def set_session(self, session):
        self.current_session = session
        helpers.show(f"Current Session is Session {session.id}", end="\n")
        return

    def _sesh(self, ID):
        '''Changes the current session to the session with the specified ID.'''
        try:
            ID = int(ID)
            self.set_session(self.sessions[ID])
            helpers.show(f"SESSION ID CHANGED TO: {ID}", colour='GREEN', style='BRIGHT', end='')
        except ValueError:
            helpers.show("INVALID SESSION ID:", colour='RED', style='BRIGHT', end='')
        return  
    
    
    #TODO:implement remove session

    def _commands(self):
        '''list the commands'''
        out = "List of Commands: | "
        for cmd in self.commands.keys():
            out += cmd + " | "
        return out

    def _hello(self):
        return "hello!"
              
    def _socket(self,port):
        '''creates a socket for the server'''
        sock =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('localhost',port))
        sock.listen(100)
        return sock
    
    def _quit(self):
        '''closes the program'''
        globals()['close'] = True
        return


    def run(self):
        #listen for incoming connections
        self.threads.append(self.get_client_connection())
        while True and not globals()['close']:
            cmd_string = input(getattr(colorama.Fore, 'GREEN') + "->" + colorama.Style.RESET_ALL)
            cmd, x, action = cmd_string.partition(' ')
            if cmd in self.commands:
                method = self.commands[cmd]['method']
                if callable(method):
                    try:
                        out = method(action) if len(action) else method()
                        if out == None:
                            out = ''
                        c = 'BLUE'
                    except Exception as e:
                        out = str(e)
                        c = 'RED'
                    helpers.show(out, colour = c,end="\n")
                
            else:
                helpers.show("INVALID COMMAND:",colour='RED', style='BRIGHT',end='')
                helpers.show("use 'commands' for list of commands", colour="BLUE")
        for t in self.threads:
            t.join()
          
if __name__ == "__main__":       

    #host the module files
    #TODO: make compatible for linux file path too
    globals()['module_host'] = subprocess.Popen('python -m http.server 5001',stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=os.getcwd() + '/modules',shell=True)

    globals()['close'] = False
    globals()['CommandServer'] = server()
    globals()['CommandServer'].run()


    #close the module host    
    process = psutil.Process(globals()['module_host'].pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()