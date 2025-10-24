import pandas as pd

def get_kma_data(stn_id):
    """
    기상청 API를 호출하여 특정 지점의 일별 데이터를 DataFrame으로 반환
    """

# API URL 
    base_url = 'https://apihub.kma.go.kr/api/typ01/url/kma_sfcdd3.php'
    tm1 = '20200101'
    tm2 = '20241231'
    authKey = 'vLfGjQIPTia3xo0CD94muA'

    # ✅ 지점 코드(stn) 포함
    url = f"{base_url}?stn={stn_id}&tm1={tm1}&tm2={tm2}&authKey={authKey}"
    try:

        # pd.read_csv로 URL에서 바로 데이터를 읽어오기.
        df = pd.read_csv(
            url,
            sep='\s+',         # 구분자: 하나 이상의 공백 (space-delimited)
            comment='#',       # '#'로 시작하는 줄은 주석으로 간주하고 무시
            header=None,       # 파일 자체에 헤더가 없다고 설정 (comment로 무시했기 때문)
            encoding='euc-kr', # 한글 인코딩
        )
        column_map = {
            0: '날짜',
            1: '지점', 
            32: '일조시간'
        }
        
        df_selected = df[column_map.keys()].rename(columns=column_map)
        
        # 3. 데이터프레임 반환
        return df_selected
    
    except Exception as e:
        print(f"데이터를 읽어오는 중 오류가 발생했습니다: {e}")
