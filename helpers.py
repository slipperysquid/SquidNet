import threading,colorama, io, os, re

def make_threaded(func):
    
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = True
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


def modify_script(original_filepath, new_filepath, custom_url,key):
    try:
        with open(original_filepath, 'r') as f_in:
            original_code = f_in.read()

        # Find the start and end indices of the original URL string
        original_url_start = original_code.find('url = f"http://127.0.0.1:5001/client.py"') 
        if original_url_start == -1:
            print("Error: Original URL not found in the file.")
            return

        
        original_url_end = original_code.find('"', original_url_start + len('url = f"')) + 1
        
        # Replace the original URL with the custom URL
        modified_code = (
            original_code[:original_url_start]
            + f'url = {custom_url}'
            + original_code[original_url_end:]
        )

        key_assignment = f"key = {repr(key)}\n"  # Encode key to bytes and add new line

        # Find a suitable place to insert the key (e.g., after imports)
        import_end = modified_code.find("import", modified_code.rfind("import"))
        if import_end !=-1:
            #find the end of the line:
            end_of_line = modified_code.find("\n", import_end)
            modified_code = (
                modified_code[:end_of_line + 1]
                + key_assignment
                + modified_code[end_of_line + 1:]
            )

        with open(new_filepath, 'w') as f_out:
            f_out.write(modified_code)

        print(f"Successfully wrote modified script to {new_filepath}")

    except FileNotFoundError:
        print(f"Error: File not found at {original_filepath}")
    except Exception as e:
        print(f"An error occurred: {e}")




def replace_host_line(file_path, new_ip):
    """
    In the given file, replace any line of the form:
        HOST = "something"
    (with optional leading spaces) with:
        HOST = "<new_ip>"
    """
    # Regex explanation:
    #  ^(\s*)         - Start of line, capture any leading spaces
    #  HOST\s*=\s*    - 'HOST' then '=' with optional spaces
    #  "([^"]*)"      - Double-quoted string containing any characters except "
    #  \s*$           - Optional trailing spaces, then end of line
    pattern = re.compile(r'^(\s*)HOST\s*=\s*"[^"]*"\s*$', re.MULTILINE)

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace with the new IP, keeping the same leading indentation
    replacement = r'\1HOST = "{}"'.format(new_ip)
    new_content = pattern.sub(replacement, content)
    # Only overwrite if something changed
    if new_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        

