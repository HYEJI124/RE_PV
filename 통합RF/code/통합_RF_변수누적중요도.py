import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import matplotlib.pyplot as plt
import os

# macOS 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# 파일 경로 설정
file_path = "/Users/parkhyeji/Desktop/RE_PV/데이터/이상치제거_후/중부+동서.csv"
save_dir = "/Users/parkhyeji/Desktop/RE_PV/RF/data/통합RF/중부+동서변수누적중요도"
os.makedirs(save_dir, exist_ok=True)
output_csv = os.path.join(save_dir, "중부+동서_RF_통합.csv")
importance_csv = os.path.join(save_dir, "중부+동서_변수중요도_통합RF.csv")
importance_img = os.path.join(save_dir, "중부+동서_변수중요도_통합RF.png")
cumulative_img = os.path.join(save_dir, "중부+동서_변수누적중요도_통합RF.png")

# CSV 읽기
df = pd.read_csv(file_path, encoding='utf-8-sig')

# 결측 처리
df['일강수량(mm)'] = df['일강수량(mm)'].fillna(0)
df = df.dropna(subset=['합계 일사량(MJ/m2)'])

# 독립변수(X), 종속변수(y)
X = df[['설비용량(MW)', '평균기온(°C)', '일강수량(mm)',
        '평균 풍속(m/s)', '평균 상대습도(%)',
        '합계 일조시간(hr)', '합계 일사량(MJ/m2)']]
y = df['발전량(MWh)']

# 학습 / 테스트 분리
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 모델 학습
model = RandomForestRegressor(n_estimators=500, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

# 예측 및 평가
y_pred = model.predict(X_test)
r2 = r2_score(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred) ** 0.5

print(f"✅ 통합 모델 R²: {r2:.4f}")
print(f"✅ 통합 모델 RMSE: {rmse:.4f}")

# ==========================================================
# 1. 결과 저장
# ==========================================================
results_df = pd.DataFrame({
    "모델": ["통합 랜덤포레스트"],
    "결정계수(R²)": [round(r2, 4)],
    "RMSE": [round(rmse, 4)],
    "데이터 수": [len(X)]
})
results_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
print(f"📁 모델 성능 결과 저장 완료: {output_csv}")

# ==========================================================
# 2. 변수 중요도 계산 및 시각화
# ==========================================================
importances = pd.Series(model.feature_importances_, index=X.columns)
importances = importances.sort_values(ascending=True)

# 중요도 DataFrame 저장
importance_df = pd.DataFrame({
    "변수명": importances.index,
    "중요도": importances.values
}).sort_values("중요도", ascending=False)
importance_df.to_csv(importance_csv, index=False, encoding='utf-8-sig')
print(f"📊 변수 중요도 저장 완료: {importance_csv}")

# 중요도 막대그래프
plt.figure(figsize=(8, 5))
bars = plt.barh(importances.index, importances.values, color='skyblue')
plt.title("변수별 중요도 (Random Forest)")
plt.xlabel("중요도")
plt.ylabel("변수명")
plt.grid(axis='x', linestyle='--', alpha=0.7)

# 막대 옆에 중요도 수치 표시
for bar in bars:
    width = bar.get_width()
    plt.text(width + 0.002, bar.get_y() + bar.get_height()/2,
             f"{width:.3f}", va='center', fontsize=10)

plt.tight_layout()
plt.savefig(importance_img, dpi=300)
plt.show()
print(f"🖼️ 변수 중요도 그래프 저장 완료: {importance_img}")

# ==========================================================
# 3. 변수 누적 중요도 (Top-N 기준)
# ==========================================================
importance_df['누적중요도(%)'] = importance_df['중요도'].cumsum() / importance_df['중요도'].sum() * 100

plt.figure(figsize=(8, 5))
plt.plot(range(1, len(importance_df) + 1),
         importance_df['누적중요도(%)'], marker='o', color='orange', linewidth=2)

plt.title("변수 누적 중요도 (Top-N 기준)")
plt.xlabel("변수 개수 (중요도 순)")
plt.ylabel("누적 중요도(%)")
plt.grid(True, linestyle='--', alpha=0.7)

# 80%, 90% 선 표시
plt.axhline(y=80, color='red', linestyle='--', linewidth=1)
plt.axhline(y=90, color='green', linestyle='--', linewidth=1)
plt.text(len(importance_df)*0.9, 80, "80%", color='red', va='bottom')
plt.text(len(importance_df)*0.9, 90, "90%", color='green', va='bottom')

for i, val in enumerate(importance_df['누적중요도(%)']):
    plt.text(i + 1, val + 1, f"{val:.1f}%", ha='center', fontsize=9)

plt.tight_layout()
plt.savefig(cumulative_img, dpi=300)
plt.show()
print(f"🖼️ 변수 누적 중요도 그래프 저장 완료: {cumulative_img}")

# ==========================================================
# 4. 실제값 vs 예측값 산점도
# ==========================================================
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
