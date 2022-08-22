import requests


r = requests.post("https://python-socket-api.herokuapp.com/api", data = {"client-id" :"1"})

print(r.text, )