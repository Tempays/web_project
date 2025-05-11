import requests

# Файл для запросов к api


URL = "http://localhost:5000/api/users/1"
SECRET_KEY = "EL_PSY_KONGROO"
headers = {
    "Authorization": f"Bearer {SECRET_KEY}"
}

response = requests.get(URL, headers=headers)

if response.status_code == 200:
    print(response.json())
else:
    print(response.status_code, response.request.url)