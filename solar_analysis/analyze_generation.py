import pandas as pd
import numpy as np
import re
from pathlib import Path

# ▶ 분석할 엑셀 파일 경로 (같은 폴더 안이므로 파일명만 써도 됨)
file_path = Path("2024_solar.xls")   # 필요하면 2020~2023으로 바꿔도 됨

# 1) 엑셀 읽기 (.xls는 xlrd 엔진 필요)
df = pd.read_excel(file_path, engine="xlrd")

# 2) 컬럼 정리
df.columns = [str(c).strip() for c in df.columns]
df = df.dropna(how="all")

# 3) '월' 컬럼 자동 탐색
month_col = None
for c in df.columns:
    if re.search(r"(월|month)", c, re.IGNORECASE):
        month_col = c
        break
if month_col is None:
    month_col = df.columns[0]

# 4) 월 숫자로 정규화
def to_month(v):
    if pd.isna(v):
        return np.nan
    s = str(v)
    m = re.search(r"(\d{1,2})", s)
    if m:
        mm = int(m.group(1))
        if 1 <= mm <= 12:
            return mm
    return np.nan

df["월"] = df[month_col].apply(to_month)

# 5) 수치형 지표 자동 탐색 (월 제외)
numeric_cols = []
for c in df.columns:
    if c == "월":
        continue
    # 콤마 제거 후 수치 변환 시도
    try:
        df[c] = pd.to_numeric(df[c].astype(str).str.replace(",", ""), errors="ignore")
    except Exception:
        pass
    if pd.api.types.is_numeric_dtype(df[c]):
        numeric_cols.append(c)

if not numeric_cols:
    raise ValueError("⚠️ 수치형 발전량 컬럼을 찾지 못했습니다. 컬럼명을 알려주시면 수정해드릴게요!")

# 6) 월별 합계
monthly = (df.groupby("월")[numeric_cols]
           .sum(min_count=1)
           .reindex(range(1, 13))
           .reset_index())

# 7) 전체 합계/평균
totals = monthly.drop(columns=["월"], errors="ignore")
overall = pd.DataFrame({
    "합계": totals.sum(numeric_only=True),
    "평균": totals.mean(numeric_only=True)
})
overall.index.name = "지표"

# 8) 결과 저장
monthly.to_csv("analysis_generation_by_month.csv", index=False, encoding="utf-8-sig")
overall.to_csv("analysis_generation_summary.csv", encoding="utf-8-sig")

print("✅ 분석 완료!")
print("💾 결과 파일:")
print(" - analysis_generation_by_month.csv (월별 합계)")
print(" - analysis_generation_summary.csv (지표별 합계·평균)")

