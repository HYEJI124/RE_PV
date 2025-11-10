import pandas as pd

# 파일 이름 정의
GEN_FILE = "한국서부발전_태양광발전.csv" # 일단 올라와있는 파일데이터 발전량(3곳)
WEATHER_FILE = "정리된_날씨데이터.csv"   # '경기', '전남' 날씨가 들어있는 파일
MAP_FILE_1 = "발전기명위치.csv"          # (사용자가 만든 파일 1)
FINAL_OUTPUT_FILE = "FINAL_DATA_merged.csv"         # 최종 저장될 파일

try:
    # ------------------------------------
    # 발전량 데이터 로드
    # ------------------------------------
    print(f"1. {GEN_FILE} 로드 중...")
    df_gen = pd.read_csv(GEN_FILE)
    print(f"   로드 완료 (총 {len(df_gen)}건)")

    # ------------------------------------
    # 2. 매핑 파일 1 (genNm -> location) 병합
    # ------------------------------------
    print(f"2. {MAP_FILE_1} 로드 및 병합 중...")
    df_map1 = pd.read_csv(MAP_FILE_1)
    
    # 'genNm' 기준으로 'location' 컬럼 추가
    df_merged1 = pd.merge(df_gen, df_map1, on='genNm', how='left')
    print(f"   'location' 컬럼 추가 완료. (예: 안산)")

    # ------------------------------------
    # 3. 매핑 파일 2 (location -> weather_region) 병합
    # ------------------------------------
    print(f"3. {MAP_FILE_2} 로드 및 병합 중...")
    df_map2 = pd.read_csv(MAP_FILE_2)
    
    # 'location' 기준으로 'weather_region' 컬럼 추가
    df_merged2 = pd.merge(df_merged1, df_map2, on='location', how='left')
    print(f"   'weather_region' 컬럼 추가 완료. (예: 경기)")

    # ------------------------------------
    # 4. 날씨 데이터 로드 및 최종 병합
    # ------------------------------------
    print(f"4. {WEATHER_FILE} 로드 중...")
    df_weather = pd.read_csv(WEATHER_FILE)
    
    # [중요] 날씨 데이터의 컬럼 이름 확인 및 변경
    # (만약 '날짜', '지역'으로 되어 있다면 'date', 'weather_region'으로 변경)
    df_weather.rename(columns={
        '날짜': 'date',  # 날씨 파일의 날짜 컬럼명
        '지역': 'weather_region' # 날씨 파일의 지역 컬럼명 ('경기', '전남' 등)
    }, inplace=True)

    print("5. 최종 병합 중... (date, weather_region 기준)")
    
    # [핵심] 'date'와 'weather_region' 2개 키로 최종 병합
    df_final = pd.merge(
        df_merged2, 
        df_weather, 
        on=['date', 'weather_region'], 
        how='left'
    )

    # ------------------------------------
    # 5. 결과 저장
    # ------------------------------------
    print(f"✅ 병합 성공! 총 {len(df_final)}건")
    print(f"   최종 컬럼: {df_final.columns.to_list()}")
    
    print(f"\n{FINAL_OUTPUT_FILE} 파일로 저장합니다...")
    df_final.to_csv(FINAL_OUTPUT_FILE, index=False, encoding='utf-8-sig')
    
    print("\n--- 작업 완료. 최종 데이터 샘플 (첫 5줄) ---")
    print(df_final.head())

except FileNotFoundError as e:
    print(f"🚨🚨🚨 오류: '{e.filename}' 파일을 찾을 수 없습니다!")
    print("스크립트와 같은 폴더에 4개 파일이 모두 있는지 확인하세요.")
except KeyError as e:
    print(f"🚨🚨🚨 오류: {e} 컬럼을 찾을 수 없습니다!")
    print("CSV 파일의 컬럼명(헤더)이 코드와 일치하는지 확인하세요.")