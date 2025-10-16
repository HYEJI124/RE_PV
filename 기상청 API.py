import requests
import pandas as pd
from io import StringIO

url = "https://apihub.kma.go.kr/api/typ01/url/kma_sfcdd3.php"
params = {
    "authKey": "vLfGjQIPTia3xo0CD94muA",  # 본인 키
    "tm1": "20200101",
    "tm2": "20201231",
    "stn": "108",
    "obs": "SS_DAY"
}

r = requests.get(url, params=params)
text = r.text

# '#' 으로 시작하는 줄 제거
clean_text = "\n".join(line for line in text.splitlines() if not line.startswith("#"))

# pandas로 읽기
df = pd.read_csv(StringIO(clean_text), delim_whitespace=True)
print(df.head())
