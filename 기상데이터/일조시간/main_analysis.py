import pandas as pd
import numpy as np
import kma_api  # kma_api.py 파일을 불러옵니다.


# --- 1. 17개 시도 지점 코드 정의 ---

''' 서울(108), 부산(159), 대구(143), 인천(112), 광주(156), 대전(133), 울산(152)
세종(239), 수원(119-경기도), 춘천(101-강원), 청주(131-충북), 홍성(177-충남),
전주(146-전북), 목포(165-전남), 안동(136-경북), 창원(155-경남), 제주(184)
'''

station_ids = [
    '108', '159', '143', '112', '156', '133', '152', '239', '119',
    '101', '131', '177', '146', '165', '136', '155', '184'
]


# --- 2. 17개 지점 데이터 반복 로딩 ---
all_weather_dfs = [] # 빈 리스트 준비
for stn_id in station_ids:
    print(f"지점 {stn_id} 데이터 로딩 중...")
    df = kma_api.get_kma_data(stn_id)
    if df is not None:
        all_weather_dfs.append(df)

if not all_weather_dfs:
    print("오류: 로드된 데이터가 없습니다.")
else:
    # --- 3. 17개 데이터를 하나로 합치기 (Concat) ---
    print("\n3. 모든 지점 데이터를 하나로 합칩니다...")
    weather_df = pd.concat(all_weather_dfs)
    
    # --- 4. 데이터 정제 (Refinement) ---
    print("4. 전체 데이터 정제를 시작합니다...")

    # [정제 1] 날짜 형식 통일
    weather_df['날짜'] = pd.to_datetime(weather_df['날짜'], format='%Y%m%d')
    # [정제 2] 결측치(-9.0) 처리
    weather_df = weather_df.replace([-9.0, -99.0, -99.9], np.nan)
    # [정제 3] '날짜'를 인덱스로 설정
    weather_df = weather_df.set_index('날짜')
    
    print("일별 데이터 정제 완료.")

    # --- 5. ✨ 지점별 + 월별 데이터로 집계 (Groupby + Resample) ---
    print("\n5. 지점별 & 월별 데이터로 집계합니다...")
    
    agg_rules = {
        '일조시간': 'sum',
        # '지점' 컬럼은 이제 groupby의 기준이므로 rules에서 빠져도 됩니다.
    }

    # (중요!) groupby('지점')으로 지점별로 그룹을 나눈 뒤,
    # 각 그룹별로 resample('M')을 적용합니다.
    monthly_df = weather_df.groupby('지점').resample('M').agg(agg_rules)
    
    # 인덱스 형식을 '2020-01'로 변경
    # (groupby를 쓰면 인덱스가 (지점, 날짜) 2중으로 잡힙니다)
    monthly_df = monthly_df.reset_index() # 2중 인덱스 풀기
    monthly_df['날짜'] = monthly_df['날짜'].dt.to_period('M')
    monthly_df = monthly_df.set_index(['지점', '날짜']) # 다시 (지점, 날짜)로 인덱스
    

    # --- 6. 최종 월별 데이터 확인 ---
    print("\n--- 최종 집계된 월별 데이터 (일부) ---")
    print(monthly_df.head(10)) # 108(서울) 데이터
    print("...")
    print(monthly_df.tail(10)) # 184(제주) 데이터






