import requests
import re

url='http://horw.space:7001/status'

files = {'file':open('send.py','rb')}
values =  {'query': 100}

r = requests.get(url,json=values)
print(r.content)