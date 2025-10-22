import pandas as pd
import numpy as np
import time
import kma_api


# 1. 17개 시도 지점 코드 정의
'''
서울(108), 부산(159), 대구(143), 인천(112), 광주(156), 대전(133), 울산(152),
세종(239), 수원(119), 춘천(101), 청주(131), 홍성(177),
전주(146), 목포(165), 안동(136), 창원(155), 제주(184)
'''
station_ids = [
    '108', '159', '143', '112', '156', '133', '152', '239', '119',
    '101', '131', '177', '146', '165', '136', '155', '184'
]


# 2. 지점별 데이터 로딩
all_weather_dfs = []      # 전체 지점 데이터 저장용
failed_stations = []      # 실패한 지점 저장용

for stn_id in station_ids:
    print(f"지점 {stn_id} 데이터 로딩 중")

    try:
        df = kma_api.get_kma_data(stn_id)

        # 유효성 검사
        if df is not None and not df.empty:
            all_weather_dfs.append(df)
        else:
            print(f"지점 {stn_id}: 빈 데이터 또는 None 반환됨.")
            failed_stations.append(stn_id)

    except Exception as e:
        print(f" 지점 {stn_id} 데이터 로딩 중 오류 발생: {e}")
        failed_stations.append(stn_id)

    time.sleep(0.5)  # API 요청 간격 조정

# 로딩 결과 요약
if failed_stations:
    print(f"다음 지점은 데이터 로딩 실패: {failed_stations}")
else:
    print("모든 지점 데이터가 정상적으로 로드되었습니다.")


# 3. 모든 지점 데이터 병합
if not all_weather_dfs:
    raise ValueError("오류: 로드된 데이터가 없습니다. (모든 요청 실패)")
else:
    weather_df = pd.concat(all_weather_dfs, ignore_index=True)


# 4. 데이터 정제
# (1) 날짜 형식 통일
weather_df['날짜'] = pd.to_datetime(weather_df['날짜'], format='%Y%m%d', errors='coerce')

# (2) 결측치(-9.0, -99.0, -99.9 등) → NaN으로 변환
weather_df = weather_df.replace([-9.0, -99.0, -99.9], np.nan)

# (3) 지점 및 날짜 기준 정렬
weather_df = weather_df.sort_values(by=['지점', '날짜'])

# (4) 인덱스 설정
weather_df = weather_df.set_index('날짜')

# 5. 지점별 & 월별 집계
# 집계 규칙 정의 (필요시 확장 가능)
agg_rules = {
    '일조시간': 'sum',
}

# groupby + resample('M')으로 월별 합계 계산
monthly_df = (
    weather_df
    .groupby('지점')
    .resample('M')
    .agg(agg_rules)
    .reset_index()
)

# 날짜를 월 단위 Period 형식으로 변환
monthly_df['날짜'] = monthly_df['날짜'].dt.to_period('M')

# 최종 인덱스 구성
monthly_df = monthly_df.set_index(['지점', '날짜'])
print(" 월별 데이터 집계 완료.")


# 6. 결과 미리보기
print("\n--- 최종 월별 집계 데이터 미리보기 ---")
print(monthly_df.head(10))
print("======================================")
print(monthly_df.tail(10))


# 7. CSV 파일로 저장시
# output_path = "monthly_weather_data.csv"
# monthly_df.to_csv(output_path, encoding='utf-8-sig')
# print(f"\n💾 CSV 파일로 저장 완료: {output_path}")
