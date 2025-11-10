import pandas as pd
import requests
import datetime

# 1. 발전소 위치 파일 읽기
try:
    df_locations = pd.read_csv("locations.csv", encoding="cp949")
    print("locations.csv 파일 읽기 성공.")

    # 2. 중복되지 않는 위도/경도 목록 생성
    unique_locations = df_locations[['발전기명', '위도', '경도']].drop_duplicates().reset_index(drop=True)
    print("\n고유한 발전소 위치 목록:")
    print(unique_locations.head())  # 상위 5개만 표시

    # 3. API 호출 설정
    base_url = "https://apihub.kma.go.kr/api/typ01/cgi-bin/url/nph_sun_nwp_txt"
    auth_key = "vLfGjQIPTia3xo0CD94muA"  # 사용자 인증키
    nwp_model = "KIMG"
    variable = "NSWRF"  # 일사량 (지표면 순단파 복사, W/m^2)
    interval = "1"      # 1시간 간격

    # 4. 동적 시간 설정 (예: '오늘'을 기준으로 '내일'을 예측)
    # KST (한국 시간) 기준
    today_kst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))

    # KIMG 모델은 00, 06, 12, 18 UTC에 실행됩니다.
    # '내일'을 예측하기 위해 '오늘 00시 UTC' (KST 09시)에 발표된 모델을 사용한다고 가정

    # 모델 기준 시간 (Base Time) - KST 09시에 발표된 모델 (00 UTC)
    tm_base_kst = today_kst.replace(hour=9, minute=0, second=0, microsecond=0)
    # 만약 현재 시간이 9시 이전이라면, 어제 9시 모델을 써야 함
    if datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))) < tm_base_kst:
        tm_base_kst = tm_base_kst - datetime.timedelta(days=1)

    # KST 기준 시간을 UTC로 변환하여 'tm' 파라미터 생성
    tm_base_utc = tm_base_kst - datetime.timedelta(hours=9)
    tm_base = tm_base_utc.strftime('%Y%m%d%H%M')  # 예: 202511070000

    # 예측할 시간 범위 (Forecast Time) - '내일' 09시부터 18시까지 (KST)
    tomorrow = today_kst + datetime.timedelta(days=1)
    tm_ef1_kst = tomorrow.replace(hour=9, minute=0)
    tm_ef2_kst = tomorrow.replace(hour=18, minute=0)

    # KST 시간을 UTC로 변환하여 tmef 파라미터 생성
    tm_ef1 = (tm_ef1_kst - datetime.timedelta(hours=9)).strftime('%Y%m%d%H%M')
    tm_ef2 = (tm_ef2_kst - datetime.timedelta(hours=9)).strftime('%Y%m%d%H%M')

    print(f"\n--- API 호출 파라미터 (예시) ---")
    print(f"모델 기준 시간 (tm, UTC): {tm_base}")
    print(f"예측 시작 시간 (tmef1, UTC): {tm_ef1}")
    print(f"예측 종료 시간 (tmef2, UTC): {tm_ef2}")
    print(f"요청 변수 (varn): {variable}")
    print("---------------------------------")

    # 5. 모든 고유 위치에 대해 API 호출 (테스트로 첫 3개만)
    all_forecast_data = {}

    for index, row in unique_locations.head(3).iterrows():
        lat = row['위도']
        lon = row['경도']
        site_name = row['발전기명']

        print(f"\n[{site_name}] 발전기명 (위도:{lat}, 경도:{lon}) API 호출 시도...")

        params = {
            'authKey': auth_key,
            'nwp': nwp_model,
            'varn': variable,
            'tm': tm_base,
            'tmef1': tm_ef1,
            'tmef2': tm_ef2,
            'int': interval,
            'lat': lat,
            'lon': lon
        }

        try:
            response = requests.get(base_url, params=params)

            if response.status_code == 200:
                print(f"[{site_name}] API 호출 성공!")
                print("--- 반환된 텍스트 데이터 (일부) ---")
                print('\n'.join(response.text.splitlines()[:5]))  # 상위 5줄만 표시

                # 나중을 위해 데이터 저장
                all_forecast_data[site_name] = response.text

            else:
                print(f"[{site_name}] API 호출 실패. 상태 코드: {response.status_code}")
                print("에러 메시지:", response.text)

        except Exception as e:
            print(f"[{site_name}] API 호출 중 오류 발생: {e}")

    print("\n--- 모든 작업 완료 ---")
    # all_forecast_data 딕셔너리에 각 지점별 예측 텍스트가 저장됩니다.
    # 다음 단계는 이 텍스트를 파싱하는 것입니다.

except FileNotFoundError:
    print("locations.csv 파일을 찾을 수 없습니다.")
except Exception as e:
    print(f"오류 발생: {e}")
