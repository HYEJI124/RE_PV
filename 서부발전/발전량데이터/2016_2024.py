import requests
import xmltodict
import json
import pandas as pd
import time
import xml.parsers.expat
from datetime import datetime

# ----------------------------------------
# 1. 기본 설정
# ----------------------------------------

# ‼️‼️ data.go.kr의 '일반 인증키(Decoded)'를 여기에 붙여넣으세요 ‼️‼️
# SERVICE_KEY = "5a102a4e417bb10c08a0f7f7798a3693f30d2fddeca3c4689abc81ea4939ab68"
# SERVICE_KEY = "a8e1d37e6bc69ccac0b101c638f05e8a83ce096c866d4448f1c56ced78b6d28f"
SERVICE_KEY = "5c2a79910d28fa8ea349b804c0c36bd86b0b6c830bae4bfc390eabe877722131"

BASE_URL = "https://apis.data.go.kr/B552522/pg/reGeneration/getReGeneration"

# 조회할 기간 설정
START_YEAR = 2019
END_YEAR = 2022

# 한 번의 API 요청으로 가져올 데이터 수 (API 최대치 100으로 설정)
NUM_OF_ROWS = 100

# 최종 저장될 파일 이름
CSV_FILE_NAME = "renewable_generation_2019_2024.csv"

# ----------------------------------------
# 2. 데이터 수집 함수
# ----------------------------------------
def fetch_data(params):
    """API를 호출하고 응답을 딕셔너리로 반환하는 함수"""
    try:
        response = requests.get(BASE_URL, params=params)
        
        # 200 (OK) 코드가 아니면 오류 발생
        if response.status_code != 200:
            print(f"    🚨 오류: 상태 코드 {response.status_code}")
            print(f"    {response.text}")
            return None
        
        # XML 파싱
        data_dict = xmltodict.parse(response.text)
        return data_dict

    except requests.exceptions.RequestException as e:
        print(f"    🚨 네트워크 오류: {e}")
        return None
    except xml.parsers.expat.ExpatError as e:
        print(f"    🚨 XML 파싱 오류: {e}")
        print(f"    --- 응답 원본 ---")
        print(response.text[:500])
        return None

# ----------------------------------------
# 3. 메인 로직 (데이터 수집 및 저장)
# ----------------------------------------
def main():
    print(f"🚀 데이터 수집을 시작합니다. ({START_YEAR}년 ~ {END_YEAR}년)")
    print(f"CSV 파일명: {CSV_FILE_NAME}\n")
    
    all_data_list = []  # 모든 'item'을 저장할 리스트
    
    # 1. 바깥쪽 루프: 연도 (2016, 2017, ...)
    for year in range(START_YEAR, END_YEAR + 1):
        
        # 2. 중간 루프: 월 (1, 2, ...)
        for month in range(1, 13):
            
            # (2024년 12월을 초과하지 않도록 함 - 예시: 2025년 1월이면 중지)
            if datetime.now().year == year and datetime.now().month < month:
                print(f"--- {year}년 {month}월: 아직 도래하지 않은 기간이므로 중지 ---")
                break
                
            # 날짜 형식 생성 (예: 20160101, 20160131)
            # pandas를 사용해 각 월의 첫날과 마지막 날을 정확히 계산
            try:
                start_date = pd.Timestamp(f"{year}-{month:02d}-01")
                end_date = start_date + pd.offsets.MonthEnd(0)
                
                # API 형식 (YYYYMMDD)으로 변환
                start_date_str = start_date.strftime('%Y%m%d')
                end_date_str = end_date.strftime('%Y%m%d')
                
                print(f"--- {year}년 {month}월 ({start_date_str} ~ {end_date_str}) 데이터 수집 ---")
            
            except ValueError:
                print(f"    ⚠️  {year}-{month:02d} 날짜 생성 오류. 건너뜁니다.")
                continue

            page_no = 1
            total_pages = 1 # 우선 1페이지로 시작
            
            # 3. 안쪽 루프: 페이지네이션 (1, 2, ...)
            while page_no <= total_pages:
                
                params = {
                    "serviceKey": SERVICE_KEY,
                    "pageNo": page_no,
                    "numOfRows": NUM_OF_ROWS,
                    "startDate": start_date_str,
                    "endDate": end_date_str
                }
                
                print(f"    {month}월 데이터 요청 중... (페이지: {page_no}/{total_pages})", end="\r")
                
                data = fetch_data(params)
                
                # 서버 부하를 줄이기 위해 매 요청마다 0.5초 대기
                time.sleep(1.5) 
                
                if data is None:
                    print(f"    🚨 {year}-{month}월 {page_no}페이지 요청 실패. 다음 월로 넘어갑니다.")
                    break # 현재 월의 수집 중단

                # --- 응답 분석 ---
                try:
                    header = data.get("response", {}).get("header")
                    body = data.get("response", {}).get("body")

                    # API 자체 오류 확인 (e.g., SERVICE KEY ERROR)
                    if header and header.get("resultCode") != "00":
                        print(f"    🚨 API 오류: {header.get('resultMsg')} (코드: {header.get('resultCode')})")
                        break # 현재 월의 수집 중단
                    
                    if body is None or "items" not in body or not body.get("items"):
                        print("    ℹ️  데이터 없음(items).")
                        break # 현재 월에 데이터가 없으므로 다음 월로

                    # --- 데이터 추출 ---
                    items_data = body["items"]["item"]
                    
                    # 데이터가 1개일 경우 dict, 여러 개일 경우 list
                    if isinstance(items_data, dict):
                        item_list = [items_data]
                    else:
                        item_list = items_data
                    
                    # 수집한 데이터를 메인 리스트에 추가
                    all_data_list.extend(item_list)
                    
                    # --- 페이지네이션 업데이트 ---
                    if page_no == 1: # 첫 페이지만 totalCount를 확인
                        total_count = int(body.get("totalCount", 0))
                        if total_count == 0:
                            print("    ℹ️  데이터 없음(totalCount: 0).")
                            break
                        
                        # (totalCount / 100)을 올림하여 전체 페이지 수 계산
                        total_pages = (total_count + NUM_OF_ROWS - 1) // NUM_OF_ROWS
                        print(f"    ✅ 총 {total_count}건 발견 (총 {total_pages}페이지)")
                    
                    page_no += 1 # 다음 페이지로
                
                except Exception as e:
                    print(f"\n    🚨 데이터 구조 파싱 중 오류: {e}")
                    print(json.dumps(data, indent=2, ensure_ascii=False)) # 오류난 부분의 JSON 구조 확인
                    break # 현재 월 중단

    # ----------------------------------------
    # 4. CSV 파일로 저장
    # ----------------------------------------
    print("\n\n🏁 모든 데이터 수집 완료.")
    
    if not all_data_list:
        print("🚨 수집된 데이터가 없습니다. CSV 파일을 생성하지 않습니다.")
    else:
        print(f"총 {len(all_data_list)}건의 데이터를 CSV 파일로 저장합니다...")
        
        try:
            # 리스트를 Pandas DataFrame으로 변환
            df = pd.DataFrame(all_data_list)
            
            # CSV로 저장 (한글 깨짐 방지를 위해 'utf-8-sig' 사용)
            df.to_csv(CSV_FILE_NAME, index=False, encoding='utf-8-sig')
            
            print(f"\n✅ 성공! '{CSV_FILE_NAME}' 파일이 생성되었습니다.")
            print("\n--- 데이터 샘플 (첫 5줄) ---")
            print(df.head())

        except Exception as e:
            print(f"🚨 CSV 파일 저장 중 오류: {e}")

# 스크립트 실행
if __name__ == "__main__":
    main()