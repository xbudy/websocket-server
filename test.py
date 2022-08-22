import requests


r = requests.post("http://localhost:8080/api", data = {"client-id" :"1"})

print(r.text, )