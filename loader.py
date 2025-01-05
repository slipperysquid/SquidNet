from urllib import request
url = f"http://127.0.0.1:5001/client.py"
exec(request.urlopen(url).read().decode('utf-8') )