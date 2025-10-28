# -------------------------------
# 1. 데이터 불러오기
# -------------------------------
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
# ✅ 한글 폰트 설정
plt.rc('font', family='Malgun Gothic')
plt.rc('axes', unicode_minus=False)

# 파일 읽기 (탭 구분 + CP949 인코딩)
df = pd.read_csv("날ㄹ씨.csv", encoding="cp949", sep="\t")

# 컬럼 정리
df.columns = df.columns.str.replace('\ufeff', '').str.strip()

# 날짜 처리
df['year'] = df['날짜'].str.extract(r'(\d{4})년').astype(int)
df['month'] = df['날짜'].str.extract(r'(\d{1,2})월').astype(int)


# 3. 범주형 인코딩
# -------------------------------
df = pd.get_dummies(df, columns=['시도'], drop_first=True)

# -------------------------------
# 4. 학습 데이터 구성
# -------------------------------
X = df[['풍속', '기온', '일조시간', '일사량', '발전설비', 'year', 'month'] +
        [col for col in df.columns if '시도_' in col]]
y = df['발전량'].replace(',', '', regex=True).astype(float)

# -------------------------------
# 5. 학습/테스트 분리 + 모델 학습
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestRegressor(random_state=42)
model.fit(X_train, y_train)

# -------------------------------
# 6. 성능 평가
# -------------------------------
y_pred = model.predict(X_test)
print("R² score:", r2_score(y_test, y_pred))
print("MAE:", mean_absolute_error(y_test, y_pred))

