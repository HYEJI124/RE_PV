import requests
import json

# URL 문자열
url = 'https://apihub.kma.go.kr/api/typ01/url/kma_sfcdd3.php?tm1=20200101&tm2=20241231&stn=108&disp=1&help=0&authKey=vLfGjQIPTia3xo0CD94muA'

# GET 요청
response = requests.get(url)

# 응답을 JSON 형태로 변환
json_response = response.json()

print(json_response)