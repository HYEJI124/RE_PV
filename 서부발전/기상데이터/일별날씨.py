import pandas as pd
import numpy as np
import time
import kma_api_hourly  # ← get_kma_data() 함수가 들어있는 파일

# --------------------------------------------------
# 1. 전국 지점 코드 (ASOS 지점 ID)
# --------------------------------------------------
station_ids = [
    # 경기도
    '98','119','202','203','99',
    # 세종특별자치시
    '239',
    # 전라남도 (❌ 이번에는 제외)
    # '259','262','266','165','164','258','174','168','252','170','260','256','175','268','261','169',
]

# --------------------------------------------------
# 2. 지점-시도 매핑 딕셔너리
# --------------------------------------------------
station_to_region = {
    '98':'경기','119':'경기','202':'경기','203':'경기','99':'경기',
    '239':'세종',
    # '259':'전남','262':'전남','266':'전남','165':'전남','164':'전남','258':'전남','174':'전남',
    # '168':'전남','252':'전남','170':'전남','260':'전남','256':'전남','175':'전남',
    # '268':'전남','261':'전남','169':'전남',
}

# --------------------------------------------------
# 3. 데이터 로딩
# --------------------------------------------------
AUTH_KEY = 'vLfGjQIPTia3xo0CD94muA'
all_weather_dfs = []
failed_stations = []

print("🌤 데이터 로딩 시작\n")

for stn_id in station_ids:
    print(f"📡 지점 {stn_id} ({station_to_region.get(stn_id)}) 로딩 중...")
    try:
        df = kma_api_hourly.get_kma_data(stn_id)

        if df is not None and not df.empty:
            # 컬럼 보정
            if '날짜' not in df.columns and '일시' in df.columns:
                df = df.rename(columns={'일시': '날짜'})

            # ✅ 시도 정보 추가
            df['시도'] = station_to_region.get(stn_id, '미분류')
            df['지점'] = stn_id

            # ✅ 컬럼명 통일 (필요 시)
            rename_dict = {
                '풍속(평균)': '풍속',
                '기온(평균)': '기온',
                '일조시간(시간)': '일조',
                '일사량(MJ/m2)': '일사'
            }
            df.rename(columns={c: rename_dict[c] for c in df.columns if c in rename_dict}, inplace=True)

            all_weather_dfs.append(df)
        else:
            print(f"⚠️ 지점 {stn_id}: 빈 데이터 또는 None 반환됨.")
            failed_stations.append(stn_id)

    except Exception as e:
        print(f"❌ 지점 {stn_id} 오류 발생: {e}")
        failed_stations.append(stn_id)

    time.sleep(0.5)  # API 요청 간격 제한 (0.5초)

if not all_weather_dfs:
    raise ValueError("❌ 모든 지점 데이터 로딩 실패!")

weather_df = pd.concat(all_weather_dfs, ignore_index=True)
print("\n✅ --- 모든 데이터 로딩 완료 ---")

# --------------------------------------------------
# 4. 데이터 정제
# --------------------------------------------------
print("🧹 데이터 정제 중...")

weather_df['날짜'] = pd.to_datetime(weather_df['날짜'], format='%Y%m%d', errors='coerce')

numeric_cols = ['풍속','풍향','기온','습도','강수량','일조','일사']
for col in numeric_cols:
    if col in weather_df.columns:
        weather_df[col] = pd.to_numeric(weather_df[col], errors='coerce')

weather_df = weather_df.replace([-9.0, -99.0, -99.9], np.nan)
weather_df = weather_df.sort_values(by=['시도','지점','날짜']).reset_index(drop=True)

print("✅ 데이터 정제 완료")

# --------------------------------------------------
# 5. 시도별 일평균 집계
# --------------------------------------------------
print("\n📊 시도별 일평균 계산 중...")

region_daily_df = (
    weather_df
    .groupby(['시도','날짜'])[numeric_cols]
    .mean()
    .reset_index()
)

print("✅ 시도별 일평균 계산 완료")
print(region_daily_df.head(10))

# --------------------------------------------------
# 6. CSV 저장
# --------------------------------------------------
output_path = '날씨데이터_일별_시도평균.csv'
region_daily_df.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f"\n💾 '{output_path}' 저장 완료!")

if failed_stations:
    print("\n⚠️ 데이터 수집 실패 지점:")
    print(failed_stations)
