import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import matplotlib.pyplot as plt
import os

# macOS 한글 폰트 설정 (그래프 깨짐 방지)
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# 파일 경로
file_path = "/Users/parkhyeji/Desktop/RE_PV/data/중부+동서/동서+중부_일사량예측(LR).csv"
output_csv = "/Users/parkhyeji/Desktop/RE_PV/data/중부+동서/동서+중부_통합학습결과_일사량LR.csv"

# CSV 읽기
df = pd.read_csv(file_path, encoding='utf-8-sig')

# 🔹 결측 처리
df['일강수량(mm)'] = df['일강수량(mm)'].fillna(0)
df = df.dropna(subset=['합계 일사량(MJ/m2)'])

# 🔹 독립변수(X), 종속변수(y)
X = df[['설비용량(MW)', '평균기온(°C)', '일강수량(mm)',
        '평균 풍속(m/s)', '평균 상대습도(%)',
        '합계 일조시간(hr)', '합계 일사량(MJ/m2)']]
y = df['발전량(MWh)']

# 🔹 학습 / 테스트 분리
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 🔹 모델 학습
model = RandomForestRegressor(n_estimators=500, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

# 🔹 예측 및 평가
y_pred = model.predict(X_test)
r2 = r2_score(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred) ** 0.5

print(f"✅ 통합 모델 R²: {r2:.4f}")
print(f"✅ 통합 모델 RMSE: {rmse:.4f}")

# 🔹 결과 저장
results_df = pd.DataFrame({
    "모델": ["통합 랜덤포레스트"],
    "결정계수(R²)": [round(r2, 4)],
    "RMSE": [round(rmse, 4)],
    "데이터 수": [len(X)]
})
results_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
print(f"📁 결과 저장 완료: {output_csv}")

# 🔹 중요 변수 시각화
importances = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)
plt.figure(figsize=(8, 5))
importances.plot(kind='barh', color='skyblue')
plt.title("특성 중요도 (Feature Importance)")
plt.xlabel("중요도")
plt.ylabel("특성")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()

# 🔹 실제값 vs 예측값 산점도
plt.figure(figsize=(6, 6))
plt.scatter(y_test, y_pred, alpha=0.5, color='royalblue')
plt.plot([y_test.min(), y_test.max()],
         [y_test.min(), y_test.max()],
         'r--', lw=2, label="완벽 예측선 (y=x)")
plt.title("테스트 데이터: 실제 발전량 vs 예측 발전량")
plt.xlabel("실제 발전량(MWh)")
plt.ylabel("예측 발전량(MWh)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
