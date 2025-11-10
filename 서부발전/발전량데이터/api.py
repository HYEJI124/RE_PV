
# SERVICE_KEY = "a8e1d37e6bc69ccac0b101c638f05e8a83ce096c866d4448f1c56ced78b6d28f"
# SERVICE_KEY = "5a102a4e417bb10c08a0f7f7798a3693f30d2fddeca3c4689abc81ea4939ab68"
import requests
import xmltodict
import json
import xml.parsers.expat

# 1️⃣ 기본 설정
SERVICE_KEY = "5a102a4e417bb10c08a0f7f7798a3693f30d2fddeca3c4689abc81ea4939ab68"
BASE_URL = "https://apis.data.go.kr/B552522/pg/reGeneration/getReGeneration"

params = {
    "serviceKey": SERVICE_KEY,
    "pageNo": 1,
    "numOfRows": 10,
    "startDate": "20230101",
    "endDate": "20230131"
}

# ----------------------------------------
# 2️⃣ API 요청
# ----------------------------------------
response = requests.get(BASE_URL, params=params)
print("📡 상태 코드:", response.status_code)

# ----------------------------------------
# 3️⃣ 상태 코드 확인 후 데이터 처리
# ----------------------------------------
if response.status_code == 200:
    try:
        data_dict = xmltodict.parse(response.text)
        json_data = json.loads(json.dumps(data_dict))

        body = json_data["response"]["body"]
        # 데이터가 없을 경우를 대비하여 .get() 사용
        items = body.get("items")

        if items:
            item_list = items['item']
            # 데이터가 1개일 경우 list가 아니므로 list로 만들어줌
            if not isinstance(item_list, list):
                item_list = [item_list]

            print(f"✅ 전체 데이터 수: {len(item_list)}")
            print("\n✅ 첫 번째 데이터:")
            print(json.dumps(item_list[0], indent=2, ensure_ascii=False))
        else:
            print("ℹ️ 조회된 데이터가 없습니다.")

    except xml.parsers.expat.ExpatError:
        print("🚨 오류: 상태 코드는 200이지만, XML 파싱에 실패했습니다.")
        print("--- 서버 응답 내용 ---")
        print(response.text)
else:
    print(f"🚨 API 요청 실패 (오류 코드: {response.status_code})")
    print("--- 서버 오류 메시지 ---")
    print(response.text)