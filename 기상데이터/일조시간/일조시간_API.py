# SERVICE_KEY = "1wLYAOOWTFKC2ADjlnxSVg"
import requests
import pandas as pd
from io import StringIO  # 텍스트 데이터를 파일처럼 다루기 위해 필요

# 1. API 요청 정보 설정
# ⚠️ 1단계에서 발급받은 '일반 인증키'를 꼭 입력하세요.
SERVICE_KEY = "1wLYAOOWTFKC2ADjlnxSVg"

# 사용자가 요청한 URL 기반으로 수정 (help=2, disp=1 로 변경)
API_URL = f"https://apihub.kma.go.kr/api/typ01/url/kma_sfcdd3.php?tm1=20200101&tm2=20241231&stn=108&disp=1&help=2&authKey={SERVICE_KEY}"

print("API 요청을 시작합니다 (5년 치 데이터, 시간이 걸릴 수 있습니다)...")

# 2. API 호출
try:
    response = requests.get(API_URL, timeout=30)  # 타임아웃을 30초로 설정

    if response.status_code == 200:
        print("✅ API 호출 성공!")

        # 3. 텍스트 데이터 파싱
        # API가 반환하는 텍스트 데이터를 가져옵니다.
        raw_text_data = response.text

        # 텍스트가 비어있는지 확인
        if not raw_text_data.strip():
            print("❌ 수신된 데이터가 비어있습니다. 인증키나 요청 기간을 확인하세요.")
        else:
            # 4. 텍스트를 Pandas DataFrame으로 바로 읽기
            # 이 API는 쉼표(,)로 구분된 CSV와 유사한 형식을 줍니다.
            # 첫 번째 줄이 헤더(컬럼명)가 아닐 수 있으므로 header=None 설정
            # 컬럼 이름은 기상청 표준에 따라 직접 지정해줘야 합니다.

            # ASOS 일자료(kma_sfcdd3)의 disp=1 출력 컬럼 이름
            # (이 순서는 기상청에서 고정)
            col_names = [
                "지점", "일시", "평균기온", "최저기온", "최저기온시각", "최고기온", "최고기온시각",
                "강수계속시간", "10분최다강수량", "10분최다강수량시각", "1시간최다강수량", "1시간최다강수량시각",
                "일강수량", "최대순간풍속", "최대순간풍속시각", "최대풍속", "최대풍속시각", "최대풍속풍향",
                "평균풍속", "풍정합", "최다풍향", "평균이슬점온도", "최소상대습도", "최소상대습도시각",
                "평균상대습도", "평균증기압", "평균현지기압", "최고해면기압", "최고해면기압시각",
                "최저해면기압", "최저해면기압시각", "평균해면기압", "가조시간", "합계일조시간", "1시간최다일사량시각",
                "1시간최다일사량", "합계일사량", "일신적설", "일최심적설", "일최심적설시각", "합계 3시간신적설",
                "평균지면온도", "최저초상온도", "평균5cm지중온도", "평균10cm지중온도", "평균20cm지중온도",
                "평균30cm지중온도", "0.5m지중온도", "1.0m지중온도", "1.5m지중온도", "3.0m지중온도", "5.0m지중온도",
                "합계대형증발량", "합계소형증발량", "9-9강수", "안개계속시간", "운형(운형약어)", "지점명"
            ]

            # StringIO를 사용해 텍스트를 파일처럼 Pandas가 읽게 함
            data_file = StringIO(raw_text_data)

            # 텍스트를 DataFrame으로 변환
            df = pd.read_csv(data_file, sep=",", names=col_names, encoding='euc-kr')

            # 5. 필요한 '일조시간' 데이터만 추출
            # '일시'와 '합계일조시간' 컬럼만 선택
            df_sunshine = df[['일시', '합계일조시간']].copy()

            # '합계일조시간' 컬럼의 데이터 타입을 숫자로 변경
            # (결측치가 있을 수 있으므로 errors='coerce' 사용)
            df_sunshine['합계일조시간'] = pd.to_numeric(df_sunshine['합계일조시간'], errors='coerce')

            # 결측치(NaN)가 된 값들을 0으로 채우기
            df_sunshine['합계일조시간'] = df_sunshine['합계일조시간'].fillna(0.0)

            # 6. 최종 결과 확인
            print("\n--- 최종 추출 데이터 (일조시간) ---")
            print(df_sunshine.head())  # 상위 5개만 출력
            print("\n...")
            print(df_sunshine.tail())  # 하위 5개만 출력
            print(f"\n총 {len(df_sunshine)}일의 데이터를 성공적으로 처리했습니다.")

    else:
        print(f"❌ API 호출 실패. 상태 코드: {response.status_code}")
        print(f"오류 메시지: {response.text}")

except requests.exceptions.Timeout:
    print("❌ 요청 시간 초과. (5년 치 데이터 요청은 시간이 오래 걸릴 수 있습니다.)")
except Exception as e:
    print(f"❌ 오류 발생: {e}")
