# 발전기별로 나누지 않고 설비용량 + 기상데이터로 다중선형회귀

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import matplotlib.pyplot as plt
import os

# macOS 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# 파일 경로
file_path = "/Users/parkhyeji/Desktop/RE_PV/이상치제거(인천,발전량0)/한국중부발전.csv"
output_csv = "/Users/parkhyeji/Desktop/RE_PV/통합선형결과/중부_통합회귀결과.csv"

# CSV 읽기
df = pd.read_csv(file_path, encoding='utf-8-sig')

# ==========================================================
# 1. 결측값 처리
# ==========================================================
# '일강수량(mm)', '평균기온(°C)', '평균 풍속(m/s)', '평균 상대습도(%)', '합계 일조시간(hr)' → 0으로 대체
cols_fill_zero = ['일강수량(mm)', '평균기온(°C)', '평균 풍속(m/s)',
                  '평균 상대습도(%)', '합계 일조시간(hr)']
df[cols_fill_zero] = df[cols_fill_zero].fillna(0)

# '합계 일사량(MJ/m2)' 결측 개수 확인
missing_solar_count = df['합계 일사량(MJ/m2)'].isna().sum()
print(f"✅ 합계 일사량(MJ/m2) 결측값 개수: {missing_solar_count}")

# '합계 일사량(MJ/m2)' 결측 행 제거
df = df.dropna(subset=['합계 일사량(MJ/m2)'])

# ==========================================================
# 2. 독립변수 / 종속변수 정의
# ==========================================================
X = df[['설비용량(MW)', '평균기온(°C)', '일강수량(mm)',
        '평균 풍속(m/s)', '평균 상대습도(%)',
        '합계 일조시간(hr)', '합계 일사량(MJ/m2)']]
y = df['발전량(MWh)']

# ==========================================================
# 3. 학습 / 테스트 데이터 분리
# ==========================================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

# ==========================================================
# 4. 모델 학습 및 평가
# ==========================================================
model = LinearRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

r2 = r2_score(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred) ** 0.5  # ✅ 버전 호환-safe

# ==========================================================
# 5. 결과 출력
# ==========================================================
print("\n===== ✅ 전체 데이터 통합 선형회귀 결과 =====")
print(f"R² (결정계수): {r2:.4f}")
print(f"RMSE (평균제곱근오차): {rmse:.4f}")
print(f"절편 (Intercept): {model.intercept_:.4f}")

coef_df = pd.DataFrame({
    "변수명": X.columns,
    "회귀계수": model.coef_
})
print("\n[회귀계수]")
print(coef_df)

# ==========================================================
# 6. 결과 저장
# ==========================================================
result_df = pd.DataFrame({
    "R²": [r2],
    "RMSE": [rmse],
    "절편": [model.intercept_]
})
for col, coef in zip(X.columns, model.coef_):
    result_df[col] = coef

result_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
print(f"\n📁 통합 회귀 결과 저장 완료: {output_csv}")

# ==========================================================
# 7. 시각화 (R², RMSE)
# ==========================================================
plt.figure(figsize=(6, 4))
plt.bar(['R²', 'RMSE'], [r2, rmse], color=['skyblue', 'salmon'])
plt.title('전체 데이터 회귀 모델 성능')
plt.ylabel('값')
plt.text(0, r2/2, f"{r2:.3f}", ha='center', fontsize=12)
plt.text(1, rmse/2, f"{rmse:.3f}", ha='center', fontsize=12)
plt.tight_layout()
plt.show()
