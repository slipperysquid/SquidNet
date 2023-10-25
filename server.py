


import threading, socket, colorama, helpers,session


def main():
    globals()['close'] = False
    globals()['CommandServer'] = server()
    globals()['CommandServer'].run()



class server():
    #TODO: implement what a "instruction" payload to send to the client is, (maybe json?, dictionarty?)
    def __init__(self, host='localhost', port = 5000, db='memory'):
        self.socket = self._socket(port)
        self.sessions = []
        self.current_session = None
        self.db = db
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
        while True:
            self.socket.settimeout(0.1)
            try:
                connection,ip = self.socket.accept()
                helpers.show("\nRECEIVED CONNECTION FROM: {}".format(ip),colour="GREEN",end="\n->")
                new_session = session.Session(connection,len(self.clients))
                self.sessions.append(new_session)
                new_session.check_connection()
            except socket.timeout:
                pass    
            if globals()['close']:
                helpers.show("STOPING LISTENING SOCKET",colour="RED",style="BRIGHT")
                break
    
    def set_session(self,session):
        self.current_session = session
        helpers.show("Current Session is Session {}".format(session.id), end="\n")
        return
    
    #changes session
    def _sesh(self, ID):
        #TODO:implement (definetly call set_session)

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
        '''creates a socket for the sever'''
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
        self.threads.append(self.get_client_connection())
        while True:
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

            if (globals()['close']):
                helpers.show("CLOSING SERVER",colour='RED',style='BRIGHT', end='\n')
                break
                

    

main()