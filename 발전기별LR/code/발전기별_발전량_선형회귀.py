# 발전기별로 나눠서 다중선형회귀

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import matplotlib.pyplot as plt
import os

# macOS 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'   # 한글 폰트
plt.rcParams['axes.unicode_minus'] = False    # 마이너스 기호 깨짐

# 파일 경로 설정
file_path = "/Users/parkhyeji/Desktop/RE_PV/이상치제거전데이터/동서/한국동서발전.csv"
output_csv = "/Users/parkhyeji/Desktop/RE_PV/동서.csv"

# CSV 읽기
df = pd.read_csv(file_path, encoding='utf-8-sig')

# 1. 일강수량 결측값을 0으로 대체
df['일강수량(mm)'] = df['일강수량(mm)'].fillna(0)

# 2. 합계 일사량 결측값 개수 세기
missing_solar_count = df['합계 일사량(MJ/m2)'].isna().sum()
print(f"합계 일사량(MJ/m2) 결측값 개수: {missing_solar_count}")

# 3. 결측값 제외
df = df.dropna(subset=['합계 일사량(MJ/m2)'])

# 4. 발전기별 회귀 분석 수행
results = []

for gen_name, group in df.groupby('발전기명'):
    X = group[['설비용량(MW)', '평균기온(°C)', '일강수량(mm)', '평균 풍속(m/s)',
               '평균 상대습도(%)', '합계 일조시간(hr)', '합계 일사량(MJ/m2)']]
    y = group['발전량(MWh)']

    X = X.dropna()
    y = y.loc[X.index]

    if len(X) < 5:
        continue

    # 학습/테스트 데이터 분리
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 모델 학습
    model = LinearRegression()
    model.fit(X_train, y_train)

    # 예측
    y_pred = model.predict(X_test)

    # 평가 지표 계산
    r2 = r2_score(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred) ** 0.5

    # 결과 저장
    result = {
        "발전기명": gen_name,
        "데이터수": len(X),
        "R²": r2,
        "RMSE": rmse,
        "절편": model.intercept_
    }

    # 회귀계수 추가
    for col, coef in zip(X.columns, model.coef_):
        result[col] = coef

    results.append(result)

# 결과를 DataFrame으로 변환
result_df = pd.DataFrame(results)

# csv 파일로 저장
result_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
print(f"\n 선형 회귀 결과 저장 완료: {output_csv}")

# 상위 일부 출력 확인
print("\n===== 회귀 분석 결과 요약 (상위 5개) =====")
print(result_df.head())

# 5. 시각화 (R², RMSE 비교)
plt.figure(figsize=(10, 5))

# R² 그래프
plt.subplot(1, 2, 1)
plt.bar(result_df['발전기명'], result_df['R²'])
plt.xticks(rotation=45, ha='right')
plt.title('발전기별 R² (설명력)')
plt.ylabel('R²')

# RMSE 그래프
plt.subplot(1, 2, 2)
plt.bar(result_df['발전기명'], result_df['RMSE'])
plt.xticks(rotation=45, ha='right')
plt.title('발전기별 RMSE (예측 오차)')
plt.ylabel('RMSE')

plt.tight_layout()
plt.show()