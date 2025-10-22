# 파일 이름: main_analysis.py

import pandas as pd
import numpy as np
import kma_api  # kma_api.py 파일을 불러옵니다.

# --- 1. 데이터 로딩 ()---
weather_df = kma_api.get_kma_data('108') # 서울 '108' 지점

if weather_df is None:
    print("기상 데이터를 불러오는 데 실패했습니다.")
else:
    print("기상 데이터 로딩 성공.")

    # --- 2. 데이터 정제 (Refinement) ---
    # [정제 1] 날짜 형식 통일
    weather_df['날짜'] = pd.to_datetime(weather_df['날짜'], format='%Y%m%d')

    # [정제 2] 결측치(-9.0) 처리 (필수!)
    weather_df = weather_df.replace([-9.0, -99.0, -99.9], np.nan)
    
    # [정제 3] '날짜'를 인덱스로 설정
    # (resample 기능은 인덱스가 날짜/시간 타입일 때만 작동합니다)
    weather_df = weather_df.set_index('날짜')

    # --- 3. 월별 데이터로 집계 (Resample) ---
    print("\n 월별 데이터로 집계")
    
    # 집계 규칙
    # - 일조시간, 일사합: 월간 총합계 (sum)
    # - 평균기온: 월간 평균 (mean)
    # - 지점: 그냥 첫 번째 값 사용 (first)
    agg_rules = {
        '일조시간': 'sum',
        '지점': 'first' 
    }
    
    # 'M': Month-End (월말 기준)
    monthly_df = weather_df.resample('M').agg(agg_rules)
    monthly_df.index = monthly_df.index.to_period('M')

    # --- 4. 최종 월별 데이터 확인 ---
    print("\n--- 최종 집계된 월별 데이터 (상위 12개) ---")
    print(monthly_df.head(12))

    print("\n--- 월별 데이터 요약 정보 ---")
    monthly_df.info()

    # (참고) 나중에 이 월별 데이터를 CSV로 저장해두고 싶으면
    # monthly_df.to_csv('monthly_kma_data_108.csv')
    # print("\n월별 데이터를 'monthly_kma_data_108.csv' 파일로 저장했습니다.")