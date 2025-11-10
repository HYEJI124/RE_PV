import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.metrics import r2_score, mean_squared_error
import matplotlib.pyplot as plt
import os

# macOS 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

file_path = "/Users/parkhyeji/Desktop/RE_PV/이상치제거(인천,발전량0)/한국중부발전.csv"
save_path = "/Users/parkhyeji/Desktop/RE_PV/중부(이상치제거)_변수검정_최적회귀.csv"

df = pd.read_csv(file_path, encoding='utf-8-sig')

# 결측 처리
df['일강수량(mm)'] = df['일강수량(mm)'].fillna(0)
df = df.dropna(subset=['합계 일사량(MJ/m2)'])
df = df.replace([np.inf, -np.inf], np.nan).dropna()

# 변수 지정
X_cols = ['설비용량(MW)', '평균기온(°C)', '일강수량(mm)',
          '평균 풍속(m/s)', '평균 상대습도(%)',
          '합계 일조시간(hr)', '합계 일사량(MJ/m2)']
y_col = '발전량(MWh)'

results = []

for gen_name, group in df.groupby('발전기명'):
    if len(group) < 10:
        continue

    X = group[X_cols]
    y = group[y_col]

    X = X.replace([np.inf, -np.inf], np.nan).dropna()
    y = y.loc[X.index]

    if len(X) < 5:
        continue

    # --------------------------
    # 1차 회귀모델
    # --------------------------
    X_const = sm.add_constant(X, has_constant='add')
    model = sm.OLS(y, X_const).fit()

    # 안전하게 const 제거
    pvalues = model.pvalues.copy()
    if 'const' in pvalues.index:
        pvalues = pvalues.drop('const')

    sig_vars = pvalues[pvalues < 0.05].index.tolist()

    # --------------------------
    # 비유의 변수 제거 후 재학습
    # --------------------------
    if len(sig_vars) == 0:
        sig_vars = X.columns.tolist()  # 모두 제거되면 전체 유지

    X_sig = sm.add_constant(X[sig_vars], has_constant='add')
    model_final = sm.OLS(y, X_sig).fit()

    # 평가 지표 계산
    y_pred = model_final.predict(X_sig)
    r2 = r2_score(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))

    # 결과 저장
    for var, coef, pval in zip(model_final.params.index, model_final.params.values, model_final.pvalues.values):
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
            'p-value': round(pval, 4),
            '유의성': sig,
            'R²': round(r2, 4),
            'RMSE': round(rmse, 4),
            '사용변수수': len(sig_vars),
            '데이터수': len(X)
        })

# 결과 저장
result_df = pd.DataFrame(results)
result_df.to_csv(save_path, index=False, encoding='utf-8-sig')
print(f"\n 결과 저장 완료: {save_path}")
print(result_df.head())

# 발전기별 R² / RMSE 시각화
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
plt.title('발전기별 RMSE (예측 오차)')
plt.ylabel('RMSE')

plt.tight_layout()
plt.show()
