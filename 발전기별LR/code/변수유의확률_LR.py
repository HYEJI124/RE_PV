import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.metrics import r2_score, mean_squared_error
import matplotlib.pyplot as plt
import os

plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

file_path = "/Users/parkhyeji/Desktop/RE_PV/이상치제거(인천,발전량0)/한국중부발전.csv"
save_path = "/Users/parkhyeji/Desktop/RE_PV/중부(이상치제거)_회귀결과.csv"

df = pd.read_csv(file_path, encoding='utf-8-sig')

# 결측치 처리
df['일강수량(mm)'] = df['일강수량(mm)'].fillna(0)
missing_solar_count = df['합계 일사량(MJ/m2)'].isna().sum()
print(f"합계 일사량(MJ/m2) 결측값 개수: {missing_solar_count}")

# 합계 일사량 결측 제거
df = df.dropna(subset=['합계 일사량(MJ/m2)'])

# 무한대 값 제거
df = df.replace([np.inf, -np.inf], np.nan).dropna()

# 분석 대상 컬럼
X_cols = ['설비용량(MW)', '평균기온(°C)', '일강수량(mm)', '평균 풍속(m/s)',
          '평균 상대습도(%)', '합계 일조시간(hr)', '합계 일사량(MJ/m2)']
y_col = '발전량(MWh)'

results = []

for gen_name, group in df.groupby('발전기명'):
    if len(group) < 10:
        continue

    X = group[X_cols]
    y = group[y_col]

    # NaN, inf 값 제거
    valid_idx = X.replace([np.inf, -np.inf], np.nan).dropna().index
    X = X.loc[valid_idx]
    y = y.loc[valid_idx]

    if len(X) < 5:
        continue

    X = sm.add_constant(X)
    model = sm.OLS(y, X).fit()

    y_pred = model.predict(X)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    r2 = r2_score(y, y_pred)

    for var, coef, pval in zip(model.params.index, model.params.values, model.pvalues.values):
        if var == 'const':
            continue
        if pval < 0.001:
            sig = '***'
        elif pval < 0.01:
            sig = '**'
        elif pval < 0.05:
            sig = '*'
        else:
            sig = ''
        results.append({
            '발전기명': gen_name,
            '변수명': var,
            '회귀계수': coef,
            'p-value': pval,
            '유의성': sig,
            'R²': r2,
            'RMSE': rmse,
            '데이터수': len(group)
        })

result_df = pd.DataFrame(results)
result_df.to_csv(save_path, index=False, encoding='utf-8-sig')
print(f"\n 회귀결과 저장 완료: {save_path}")
print(result_df.head())

# 시각화
summary_df = result_df[['발전기명', 'R²', 'RMSE']].drop_duplicates()

plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.bar(summary_df['발전기명'], summary_df['R²'], color='skyblue')
plt.xticks(rotation=45, ha='right')
plt.title('발전기별 결정계수 (R²)')
plt.ylabel('R²')

plt.subplot(1, 2, 2)
plt.bar(summary_df['발전기명'], summary_df['RMSE'], color='salmon')
plt.xticks(rotation=45, ha='right')
plt.title('발전기별 RMSE')
plt.ylabel('RMSE')
plt.tight_layout()
plt.show()
