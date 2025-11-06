import pandas as pd

def get_kma_data(stn_id):
    """
    기상청 API를 호출하여 특정 지점의 일별 데이터를 DataFrame으로 반환
    """
    base_url = 'https://apihub.kma.go.kr/api/typ01/url/kma_sfcdd3.php'
    tm1 = '20220101'
    tm2 = '20241231'
    authKey = 'vLfGjQIPTia3xo0CD94muA'

    url = f"{base_url}?stn={stn_id}&tm1={tm1}&tm2={tm2}&help=1&authKey={authKey}"

    try:
        # ✅ 데이터 요청
        df = pd.read_csv(
            url,
            sep=r'\s+',         # 구분자: 하나 이상의 공백
            comment='#',       
            header=None,       
            encoding='euc-kr'
        )

        # ✅ 컬럼 인덱스 매핑 (일자료 기준)
        column_map = {
            0: '날짜',
            1: '지점',
            2: '풍속',
            10: '기온',     
            18: '습도',     
            38: '강수량',    
            32: '일조',     
            35: '일사'
            # 기온 풍속 강수량 일조시간 일사량 습도 
        }

          # ✅ 실제 존재하는 컬럼만 선택
        valid_cols = [col for col in column_map.keys() if col in df.columns]
        df_selected = df[valid_cols].rename(columns=column_map)

        # ✅ 날짜 필터 및 타입 변환
        df_selected = df_selected.dropna(subset=['날짜'])
        df_selected['날짜'] = df_selected['날짜'].astype(str)

        print(f"\n📋 컬럼 매핑 후 컬럼 목록: {list(df_selected.columns)}")
        print(f"📊 {stn_id} 지점 데이터 {len(df_selected)}행 로드 완료\n")
        print(df_selected.head())

        return df_selected

    except Exception as e:
        print(f"❌ 데이터 읽기 오류 발생: {e}")
        return pd.DataFrame()  # 빈 DF 반환


df_test = get_kma_data('108') 