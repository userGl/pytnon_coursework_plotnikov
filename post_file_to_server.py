import requests

url = 'http://127.0.0.1:8000/upload/'
files = {'file': open('test_picture.png', 'rb')}  # Specify the file you want to upload

response = requests.post(url, files=files)

print(response.text)