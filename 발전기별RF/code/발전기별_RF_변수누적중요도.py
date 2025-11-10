import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import matplotlib.pyplot as plt
import os
import numpy as np

# ✅ macOS 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# 🔹 파일 경로
file_path = "/Users/parkhyeji/Desktop/RE_PV/데이터/이상치제거_후/한국동서발전.csv"
output_csv = "/Users/parkhyeji/Desktop/RE_PV/RF/data/발전기별RF/동서_RF_발전기별_학습결과.csv"
output_folder = "/Users/parkhyeji/Desktop/RE_PV/RF/data/발전기별RF/동서_RF_발전기별_그래프"
importance_csv = "/Users/parkhyeji/Desktop/RE_PV/RF/data/발전기별RF/동서_RF_변수누적중요도.csv"

# 🔹 폴더 없으면 생성
os.makedirs(output_folder, exist_ok=True)

# 🔹 데이터 불러오기
df = pd.read_csv(file_path, encoding='utf-8-sig')

# 🔹 결측 처리
df['일강수량(mm)'] = df['일강수량(mm)'].fillna(0)
df = df.dropna(subset=['합계 일사량(MJ/m2)'])

# 🔹 사용 변수 목록
features = ['설비용량(MW)', '평균기온(°C)', '일강수량(mm)',
            '평균 풍속(m/s)', '평균 상대습도(%)',
            '합계 일조시간(hr)', '합계 일사량(MJ/m2)']

# ======================================================
# 🔹 결과 저장용 리스트
# ======================================================
results = []
all_importances = []   # 전체 발전기 중요도 누적용

# ======================================================
# 🔹 발전기명별 반복 학습
# ======================================================
for gen_name, group in df.groupby('발전기명'):
    if len(group) < 10:
        print(f"⚠️ {gen_name}: 데이터가 너무 적어 학습 건너뜀 ({len(group)}개)")
        continue

    X = group[features]
    y = group['발전량(MWh)']

    # 학습/테스트 분리
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # 모델 학습
    model = RandomForestRegressor(n_estimators=500, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    # 예측 및 평가
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred) ** 0.5

    print(f"✅ {gen_name}: R²={r2:.4f}, RMSE={rmse:.4f}, 데이터수={len(group)}")

    # 결과 누적
    results.append({
        '발전기명': gen_name,
        'R²': round(r2, 4),
        'RMSE': round(rmse, 4),
        '데이터 수': len(group)
    })

    # ======================================================
    # 🔸 (1) 실제 vs 예측 산점도
    # ======================================================
    plt.figure(figsize=(6, 6))
    plt.scatter(y_test, y_pred, alpha=0.6, color='royalblue')
    plt.plot([y_test.min(), y_test.max()],
             [y_test.min(), y_test.max()],
             'r--', lw=2, label='완벽 예측선 (y=x)')
    plt.title(f"[{gen_name}] 실제 vs 예측 발전량")
    plt.xlabel("실제 발전량(MWh)")
    plt.ylabel("예측 발전량(MWh)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, f"{gen_name}_산점도.png"), dpi=300)
    plt.close()

    # ======================================================
    # 🔸 (2) 변수 중요도 시각화
    # ======================================================
    importances = model.feature_importances_
    importance_df = pd.DataFrame({
        '변수명': features,
        '중요도': importances
    }).sort_values(by='중요도', ascending=True)

    plt.figure(figsize=(7, 5))
    plt.barh(importance_df['변수명'], importance_df['중요도'], color='seagreen')
    plt.title(f"[{gen_name}] 변수 중요도")
    plt.xlabel("중요도")
    plt.ylabel("변수명")
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, f"{gen_name}_변수중요도.png"), dpi=300)
    plt.close()

    # 🔹 전체 누적용 저장
    all_importances.append(importances)

# ======================================================
# 🔹 발전기별 결과 저장
# ======================================================
results_df = pd.DataFrame(results)
results_df.to_csv(output_csv, index=False, encoding='utf-8-sig')

# ======================================================
# 🔹 전체 발전기 평균 변수 중요도 계산
# ======================================================
if all_importances:
    avg_importances = np.mean(all_importances, axis=0)
    total_importance_df = pd.DataFrame({
        '변수명': features,
        '평균 중요도': avg_importances
    }).sort_values(by='평균 중요도', ascending=True)

    # CSV 저장
    total_importance_df.to_csv(importance_csv, index=False, encoding='utf-8-sig')

    # 그래프 저장
    plt.figure(figsize=(7, 5))
    plt.barh(total_importance_df['변수명'], total_importance_df['평균 중요도'], color='darkorange')
    plt.title("[전체 발전기] 변수 누적 중요도 (평균)")
    plt.xlabel("평균 중요도")
    plt.ylabel("변수명")
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, "전체_변수누적중요도.png"), dpi=300)
    plt.close()

    print(f"\n📊 전체 발전기 평균 변수 중요도 저장 완료: {importance_csv}")

print(f"\n📁 발전기별 결과 저장 완료: {output_csv}")
print(f"🖼️ 그래프 저장 폴더: {output_folder}")
