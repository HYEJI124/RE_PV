# -*- coding: utf-8 -*-
"""
통합 랜덤포레스트 학습 + 변수 중요도 기반 후진제거 실험
- 전체 통합 데이터로 RandomForest 학습
- 변수 중요도 계산 및 누적 중요도 그래프
- 중요도 낮은 순서대로 변수 제거하며 R² / RMSE 변화 분석
"""

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import matplotlib.pyplot as plt
import os
import numpy as np

# macOS 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# ======================================================
# 경로 설정
# ======================================================
file_path = "/Users/parkhyeji/Desktop/RE_PV/데이터/이상치제거_후/중부+동서.csv"
save_dir = "/Users/parkhyeji/Desktop/RE_PV/RF/data/통합RF/중부+동서_변수후진제거"
os.makedirs(save_dir, exist_ok=True)

# 저장 파일
output_csv = os.path.join(save_dir, "중부+동서_RF_통합결과.csv")
importance_csv = os.path.join(save_dir, "중부+동서_변수중요도.csv")
importance_img = os.path.join(save_dir, "중부+동서_변수중요도.png")
cumulative_img = os.path.join(save_dir, "중부+동서_변수누적중요도.png")
elimination_csv = os.path.join(save_dir, "중부+동서_변수제거_결과.csv")
r2_plot = os.path.join(save_dir, "중부+동서_R2변화.png")
rmse_plot = os.path.join(save_dir, "중부+동서_RMSE변화.png")

# ======================================================
# 데이터 로드 및 전처리
# ======================================================
df = pd.read_csv(file_path, encoding='utf-8-sig')
df['일강수량(mm)'] = df['일강수량(mm)'].fillna(0)
df = df.dropna(subset=['합계 일사량(MJ/m2)'])

X = df[['설비용량(MW)', '평균기온(°C)', '일강수량(mm)',
        '평균 풍속(m/s)', '평균 상대습도(%)',
        '합계 일조시간(hr)', '합계 일사량(MJ/m2)']]
y = df['발전량(MWh)']

# 학습/테스트 분리
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ======================================================
# 1. 기본 모델 학습
# ======================================================
model = RandomForestRegressor(n_estimators=500, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

r2 = r2_score(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred) ** 0.5

print(f" 통합 모델 R²: {r2:.4f}")
print(f" 통합 모델 RMSE: {rmse:.4f}")

results_df = pd.DataFrame({
    "모델": ["통합 RandomForest"],
    "결정계수(R²)": [round(r2, 4)],
    "RMSE": [round(rmse, 4)],
    "데이터 수": [len(X)]
})
results_df.to_csv(output_csv, index=False, encoding='utf-8-sig')

# ======================================================
# 2. 변수 중요도 및 누적 중요도
# ======================================================
importances = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)

importance_df = pd.DataFrame({
    "변수명": importances.index,
    "중요도": importances.values
})
importance_df.to_csv(importance_csv, index=False, encoding='utf-8-sig')

# 중요도 막대 그래프
plt.figure(figsize=(8, 5))
bars = plt.barh(importance_df['변수명'][::-1], importance_df['중요도'][::-1], color='skyblue')
plt.title("변수별 중요도 (통합 RandomForest)")
plt.xlabel("중요도")
plt.grid(axis='x', linestyle='--', alpha=0.7)
for bar in bars:
    width = bar.get_width()
    plt.text(width + 0.002, bar.get_y() + bar.get_height()/2,
             f"{width:.3f}", va='center', fontsize=10)
plt.tight_layout()
plt.savefig(importance_img, dpi=300)
plt.close()

# 누적 중요도 계산
importance_df['누적중요도(%)'] = importance_df['중요도'].cumsum() / importance_df['중요도'].sum() * 100

plt.figure(figsize=(8, 5))
plt.plot(range(1, len(importance_df) + 1),
         importance_df['누적중요도(%)'], marker='o', color='orange', linewidth=2)
plt.title("변수 누적 중요도 (Top-N 기준)")
plt.xlabel("변수 개수 (중요도 순)")
plt.ylabel("누적 중요도(%)")
plt.axhline(y=80, color='red', linestyle='--', linewidth=1)
plt.axhline(y=90, color='green', linestyle='--', linewidth=1)
plt.text(len(importance_df)*0.9, 80, "80%", color='red', va='bottom')
plt.text(len(importance_df)*0.9, 90, "90%", color='green', va='bottom')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(cumulative_img, dpi=300)
plt.close()

# ======================================================
# 3. 변수 제거 실험 (중요도 낮은 순서부터 제거)
# ======================================================
sorted_features = list(importances.sort_values(ascending=True).index)  # 낮은순 정렬
remaining_features = list(X.columns)

r2_scores = []
rmse_scores = []
feature_counts = []
used_features = []

for step in range(len(sorted_features)):
    # 모델 학습
    X_train_sub = X_train[remaining_features]
    X_test_sub = X_test[remaining_features]

    model_sub = RandomForestRegressor(n_estimators=500, random_state=42, n_jobs=-1)
    model_sub.fit(X_train_sub, y_train)
    y_pred_sub = model_sub.predict(X_test_sub)

    r2_sub = r2_score(y_test, y_pred_sub)
    rmse_sub = mean_squared_error(y_test, y_pred_sub) ** 0.5

    r2_scores.append(r2_sub)
    rmse_scores.append(rmse_sub)
    feature_counts.append(len(remaining_features))
    used_features.append(", ".join(remaining_features))

    print(f"변수 {len(remaining_features)}개 → R²={r2_sub:.4f}, RMSE={rmse_sub:.4f}")

    # 다음 단계: 가장 중요도 낮은 변수 제거
    if step < len(sorted_features) - 1:
        remove_var = sorted_features[step]
        remaining_features.remove(remove_var)

# ======================================================
# 4. 결과 저장 및 시각화
# ======================================================
elim_df = pd.DataFrame({
    "남은 변수 수": feature_counts,
    "사용 변수": used_features,
    "R²": r2_scores,
    "RMSE": rmse_scores
})
elim_df.to_csv(elimination_csv, index=False, encoding='utf-8-sig')
print(f"\n 변수 제거 실험 결과 저장 완료: {elimination_csv}")

# R² 변화 그래프
plt.figure(figsize=(7, 5))
plt.plot(feature_counts, r2_scores, 'o-', color='blue', label='R²')
plt.title("변수 제거에 따른 성능 변화 (R²)")
plt.xlabel("남은 변수 수")
plt.ylabel("R²")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(r2_plot, dpi=300)
plt.close()

# RMSE 변화 그래프
plt.figure(figsize=(7, 5))
plt.plot(feature_counts, rmse_scores, 'o-', color='red', label='RMSE')
plt.title("변수 제거에 따른 성능 변화 (RMSE)")
plt.xlabel("남은 변수 수")
plt.ylabel("RMSE")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(rmse_plot, dpi=300)
plt.close()

print(f" 성능 변화 그래프 저장 완료: {r2_plot}, {rmse_plot}")

# ======================================================
# 5. 실제 vs 예측 산점도
# ======================================================
plt.figure(figsize=(6, 6))
plt.scatter(y_test, y_pred, alpha=0.5, color='royalblue')
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()],
         'r--', lw=2, label="완벽 예측선 (y=x)")
plt.title("테스트 데이터: 실제 발전량 vs 예측 발전량")
plt.xlabel("실제 발전량(MWh)")
plt.ylabel("예측 발전량(MWh)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
