import kma_api  # 1. API 파일 import
import pandas as pd

# (나중에 사용할 분석 라이브러리들...)
# import matplotlib.pyplot as plt
# from sklearn.linear_model import LinearRegression

# --- 1. 데이터 가져오기 (복잡한 과정 숨김) ---
print("일조시간 데이터를 가져옵니다...")
# kma_api 파일 안의 함수를 호출합니다.
seoul_data = kma_api.get_kma_sunshine_data(
    start_date="20200101", 
    end_date="20241231", 
    station_id="108"
)

# --- 2. 데이터 분석 및 활용 ---
if seoul_data is not None:
    print("\n--- 서울 일조시간 데이터 (5년치) ---")
    print(seoul_data.head())
    
    # 이제 seoul_data를 가지고 회귀분석, 합치기, 시각화 등을 수행합니다.
    # 예: 월별 합계 계산
    seoul_data['일시'] = pd.to_datetime(seoul_data['일시'])
    monthly_sum = seoul_data.groupby(seoul_data['일시'].dt.to_period('M'))['합계일조시간'].sum()
    
    print("\n--- 월별 합계 ---")
    print(monthly_sum.tail())
    
else:
    print("데이터를 가져오는데 실패했습니다. kma_api.py를 확인하세요.")