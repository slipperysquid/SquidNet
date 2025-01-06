from urllib import request
url = f"http://127.0.0.1:5001/client.py"
module = request.urlopen(url).read().decode('utf-8') 
print(module)
exec(module)