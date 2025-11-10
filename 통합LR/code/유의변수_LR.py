import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import os

# macOS 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# 파일 경로 설정
file_path = "/Users/parkhyeji/Desktop/RE_PV/데이터/이상치제거_후/한국중부발전.csv"
output_csv = "/Users/parkhyeji/Desktop/RE_PV/통합LR/data/최적회귀/중부_최적회귀.csv"

# CSV 읽기
df = pd.read_csv(file_path, encoding='utf-8-sig')

# ==========================================================
# 1. 결측값 처리
# ==========================================================
cols_fill_zero = ['일강수량(mm)', '평균기온(°C)', '평균 풍속(m/s)', 
                  '평균 상대습도(%)', '합계 일조시간(hr)']
df[cols_fill_zero] = df[cols_fill_zero].fillna(0)

missing_solar_count = df['합계 일사량(MJ/m2)'].isna().sum()
print(f" 합계 일사량(MJ/m2) 결측값 개수: {missing_solar_count}")

df = df.dropna(subset=['합계 일사량(MJ/m2)'])

# ==========================================================
# 2. 회귀모델 설정 (전체 데이터 기준)
# ==========================================================
X = df[['설비용량(MW)', '평균기온(°C)', '일강수량(mm)',
        '평균 풍속(m/s)', '평균 상대습도(%)', 
        '합계 일조시간(hr)', '합계 일사량(MJ/m2)']]
y = df['발전량(MWh)']

# 상수항 추가 (statsmodels는 수동 추가 필요)
X_const = sm.add_constant(X)

# 모델 적합
model = sm.OLS(y, X_const).fit()

# ==========================================================
# 3. p-value 및 회귀결과 요약
# ==========================================================
print("\n===== 전체 데이터 회귀 결과 =====")
print(model.summary())

# p-value 추출
pvalues = model.pvalues.drop('const')
pvalue_df = pd.DataFrame({
    '변수명': pvalues.index,
    'p-value': pvalues.values
})

# 유의한 변수 (p < 0.05)
significant_vars = pvalue_df[pvalue_df['p-value'] < 0.05]['변수명'].tolist()
print(f"\n 유의한 변수 (p < 0.05): {significant_vars}")

# ==========================================================
# 4. 유의한 변수로 재회귀
# ==========================================================
if len(significant_vars) > 0:
    X_sig = sm.add_constant(X[significant_vars])
    model_sig = sm.OLS(y, X_sig).fit()
    r2_before = model.rsquared
    r2_after = model_sig.rsquared
else:
    print("유의한 변수가 없습니다. 기존 모델만 사용합니다.")
    X_sig = X_const
    model_sig = model
    r2_before = r2_after = model.rsquared

# ==========================================================
# 5. 결과 저장
# ==========================================================
result_df = pd.DataFrame({
    '단계': ['기존 모델', '유의 변수 모델'],
    '사용 변수': [', '.join(X.columns), ', '.join(significant_vars) if significant_vars else '없음'],
    'R²': [r2_before, r2_after],
    'RMSE(참고용)': [None, None]
})

# p-value 결과도 병합
final_df = pd.concat([result_df, pvalue_df], axis=0)

# CSV 저장
final_df.to_csv(output_csv, index=False, encoding='utf-8-sig')

print(f"\n 회귀결과 및 p-value 저장 완료: {output_csv}")

# ==========================================================
# 6. 시각화 (R² 전후 비교)
# ==========================================================
plt.figure(figsize=(6, 4))
plt.bar(['기존 모델', '유의 변수 모델'], [r2_before, r2_after], color=['skyblue', 'lightgreen'])
plt.title('R² 비교 (전체 vs 유의 변수만)')
plt.ylabel('R² (결정계수)')
plt.text(0, r2_before/2, f"{r2_before:.3f}", ha='center', fontsize=12)
plt.text(1, r2_after/2, f"{r2_after:.3f}", ha='center', fontsize=12)
plt.tight_layout()
plt.show()
