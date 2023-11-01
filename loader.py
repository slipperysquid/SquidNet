import os
from urllib.request import urlopen
import importlib
#this file will load and remotely import modules from a url
#TODO:NEEDS DO BE IMPLEMENTED INTO THE CLIENT

def import_from_string(content, module_name, file_name=None):
    if not file_name:
        file_name = '{0}.py'.format(module_name)
        
    value = compile(content, file_name, 'exec')
    module = importlib.new_module(module_name)
    exec (value, module.__dict__)
    return module

def import_from_url(url, module_name=None):
    file_name = os.path.basename(url).lower()
    if not module_name:
        module_name = os.path.splitext(file_name)[0]

    return import_from_string(urlopen(url).read(), module_name, file_name=file_name)