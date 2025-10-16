import requests
import json

# 1. 내 정보 설정
# 마이페이지에서 발급받은 본인의 API 인증키를 붙여넣으세요.
my_api_key = "여기에_발급받은_인증키를_붙여넣으세요" 

# 2. 요청할 주소(URL) 만들기
# API 문서(메뉴판)를 보고 어떤 정보를 요청할지 정합니다.
# 여기서는 2023년(year=2023), 서울특별시(metroCd=11), 태양광(genSrcCd=1) 정보를 요청합니다.
url = f"https://bigdata.kepco.co.kr/openapi/v1/renewEnergy.do?year=2023&metroCd=11&genSrcCd=1&apiKey={my_api_key}&returnType=json"

# 3. API 호출 (식당에 주문하기)
# requests.get() 함수를 이용해 위에서 만든 주소로 데이터를 요청합니다.
response = requests.get(url)

# 4. 응답 데이터 확인 (주문한 음식 받기)
# 서버가 보내준 응답(response)을 컴퓨터가 다루기 쉬운 JSON 형태로 변환합니다.
data = response.json()

# 5. 결과 출력
# 보기 좋게 정리해서 화면에 출력합니다.
print(json.dumps(data, indent=2, ensure_ascii=False))