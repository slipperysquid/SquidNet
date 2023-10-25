import threading,colorama

def make_threaded(func):
    
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread 
    return wrapper


def show(out, colour = None, style = None, end = ''): 
    out = str(out)
    _colour = ''
    if colour != None: 
        _colour = getattr(colorama.Fore, colour.upper()) 
    _style = '' 
    if style != None: 
        _style = getattr(colorama.Style, style.upper()) 
    print(_colour + _style + out + colorama.Style.RESET_ALL,end=end)