import requests
import re

url='http://horw.space:7001/upload'

files = {'file':open('test.jpg','rb')}
values =  {'height': 100, 'width': 100}

r = requests.post(url,files=files,data=values)
if r.status_code!=410:
	headers = r.headers['content-disposition']
	fname = re.findall("filename=(.+)", headers)[0]
	with open('appvelox_'+fname, '+wb') as f:
	    f.write(r.content)