import pandas as pd

# API URL 
url = 'https://apihub.kma.go.kr/api/typ01/url/kma_sfcdd3.php?tm1=20200101&tm2=20241231&stn=108&authKey=vLfGjQIPTia3xo0CD94muA'

try:
    # pd.read_csv로 URL에서 바로 데이터를 읽어오기.
    df = pd.read_csv(
        url,
        sep='\s+',         # 구분자: 하나 이상의 공백 (space-delimited)
        comment='#',       # '#'로 시작하는 줄은 주석으로 간주하고 무시
        header=None,       # 파일 자체에 헤더가 없다고 설정 (comment로 무시했기 때문)
        encoding='euc-kr', # 한글 인코딩
    )
    
    # 필요한 컬럼, 인덱스로 선택
    df_selected = df[[0, 1, 32]]
    df_selected.columns = ['날짜', '지점', '일조시간'] # 선택한 컬럼에만 이름 붙이기
    df_final = df_selected.set_index('날짜')
    print(df_final.head())

except Exception as e:
    print(f"데이터를 읽어오는 중 오류가 발생했습니다: {e}")
