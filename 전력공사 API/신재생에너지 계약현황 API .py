import requests
import pandas as pd

# 1. API 인증키와 요청 주소 설정
# KEPCO 빅데이터 플랫폼 '마이페이지'에서 발급받은 본인의 인증키를 붙여넣으세요!
MY_API_KEY ="f0i85SeTfHVIblg2C4HhKSNI9094P41km40l2W7z"

# 요청하고 싶은 데이터의 조건을 URL 파라미터로 설정합니다.
# year: 2023년, metroCd: 11(서울), genSrcCd: 1(태양광)
url = f'https://bigdata.kepco.co.kr/openapi/v1/renewEnergy.do?year=2019&metroCd=11&genSrcCd=1&apiKey={MY_API_KEY}=xxx&returnType=json'


# 2. API 호출하여 데이터 요청하기 🚀
print("KEPCO 서버에 데이터를 요청합니다...")
response = requests.get(url)


# 3. 응답 결과 확인 및 표로 변환하기 📊
# 서버가 응답을 성공적으로 보냈는지 확인 (상태 코드 200 = 성공)
if response.status_code == 200:
    print("데이터를 성공적으로 받아왔습니다!")
    
    # JSON 형식의 데이터를 파이썬 딕셔너리로 변환
    data = response.json()
    
    # 실제 데이터 부분('data' 키 값)을 판다스 DataFrame(표)으로 변환
    df = pd.DataFrame(data['data'])
    
    # 결과 출력
    print("\n[서울시 태양광 설비 정보]")
    print(df)

else:
    print(f"오류가 발생했습니다. (오류 코드: {response.status_code})")
    print("API 인증키가 정확한지, 요청 주소에 오타가 없는지 확인해 보세요.")