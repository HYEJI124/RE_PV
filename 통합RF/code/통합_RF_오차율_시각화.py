import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# 파일 경로
file_path = "/Users/parkhyeji/Desktop/RE_PV/이상치제거/한국중부발전.csv"
output_csv = "/Users/parkhyeji/Desktop/RE_PV/파일/중부_통합학습결과.csv"
error_csv = "/Users/parkhyeji/Desktop/RE_PV/파일/중부_발전기별_오차율.csv"

# CSV 읽기
df = pd.read_csv(file_path, encoding='utf-8-sig')

# 결측 처리
df['일강수량(mm)'] = df['일강수량(mm)'].fillna(0)
df = df.dropna(subset=['합계 일사량(MJ/m2)'])

# X, y, 인덱스 분리
X = df[['설비용량(MW)', '평균기온(°C)', '일강수량(mm)',
        '평균 풍속(m/s)', '평균 상대습도(%)',
        '합계 일조시간(hr)', '합계 일사량(MJ/m2)']]
y = df['발전량(MWh)']
idx = df.index  # 원래 인덱스 보존

# 학습 / 테스트 분리 (인덱스 포함)
X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
    X, y, idx, test_size=0.2, random_state=42
)

# 모델 학습
model = RandomForestRegressor(n_estimators=500, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

# 예측 및 평가
y_pred = model.predict(X_test)
r2 = r2_score(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred) ** 0.5

print(f"통합 모델 R²: {r2:.4f}")
print(f"통합 모델 RMSE: {rmse:.4f}")

# 결과 저장
results_df = pd.DataFrame({
    "모델": ["통합 랜덤포레스트"],
    "결정계수(R²)": [round(r2, 4)],
    "RMSE": [round(rmse, 4)],
    "데이터 수": [len(X)]
})
results_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
print(f" 결과 저장 완료: {output_csv}")

# 중요 변수 시각화
importances = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)
plt.figure(figsize=(8, 5))
importances.plot(kind='barh', color='skyblue')
plt.title("특성 중요도 (Feature Importance)")
plt.xlabel("중요도")
plt.ylabel("특성")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()

# 실제값 vs 예측값 비교 시각화
plt.figure(figsize=(8, 6))
plt.scatter(y_test, y_pred, color='royalblue', alpha=0.6, edgecolor='k')
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()],
         'r--', lw=2, label='y = x (완벽 예측선)')
plt.title("실제 발전량 vs 예측 발전량")
plt.xlabel("실제 발전량 (MWh)")
plt.ylabel("예측 발전량 (MWh)")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

# 발전기별 오차율 및 오차값 계산
if '발전기명' in df.columns:
    test_df = df.loc[idx_test].copy()
    test_df['예측 발전량(MWh)'] = y_pred
    test_df['오차값(MWh)'] = test_df['예측 발전량(MWh)'] - test_df['발전량(MWh)']
    test_df['오차율(%)'] = abs(test_df['오차값(MWh)']) / test_df['발전량(MWh)'] * 100

    # 발전기별 평균 오차율 및 오차값
    gen_error = (
        test_df.groupby('발전기명')
        .agg({'오차율(%)': 'mean', '오차값(MWh)': 'mean'})
        .reset_index()
        .sort_values('오차율(%)')
    )

    gen_error.to_csv(error_csv, index=False, encoding='utf-8-sig')
    print(f"발전기별 평균 오차율 및 오차값 저장 완료: {error_csv}")

    # 발전기별 오차율 시각화
    plt.figure(figsize=(10, 6))
    plt.barh(gen_error['발전기명'], gen_error['오차율(%)'], color='salmon')
    plt.title("발전기별 평균 오차율(%)")
    plt.xlabel("평균 오차율(%)")
    plt.ylabel("발전기명")
    plt.tight_layout()
    plt.show()

    # 발전기별 실제 vs 예측 비교 (상위 10개만 표시)
    top10 = test_df.groupby('발전기명').head(1).reset_index(drop=True).head(10)
    plt.figure(figsize=(10, 6))
    plt.bar(top10['발전기명'], top10['발전량(MWh)'], label='실제값', alpha=0.7)
    plt.bar(top10['발전기명'], top10['예측 발전량(MWh)'], label='예측값', alpha=0.7)
    plt.xticks(rotation=45, ha='right')
    plt.title("발전기별 실제값 vs 예측값 (샘플 10개)")
    plt.ylabel("발전량(MWh)")
    plt.legend()
    plt.tight_layout()
    plt.show()

else:
    print("데이터에 '발전기명' 열이 없어 오차율 계산을 생략합니다.")
