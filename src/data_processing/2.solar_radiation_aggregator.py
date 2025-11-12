import pandas as pd

# 파일 경로
file1_path = "/Users/parkhyeji/Desktop/PV/data/raw/발전소별_일사량.csv"         # 참조 파일
file2_path = "/Users/parkhyeji/Desktop/PV/data/raw/발전량기상데이터(병합).csv"       # 기준 파일
output_path = "/Users/parkhyeji/Desktop/PV/data/processed/발전량+기상.csv"

# 파일 읽기 (인코딩 감안)
df_ref = pd.read_csv(file1_path, encoding='EUC-KR')       # 참조 파일
df_target = pd.read_csv(file2_path, encoding='UTF-8-SIG') # 기준 파일

# 날짜 형식 통일
df_ref['날짜'] = pd.to_datetime(df_ref['날짜'], errors='coerce').dt.strftime('%Y-%m-%d')
df_target['날짜'] = df_target['날짜'].astype(str).str.replace('.', '-').str.replace('--', '-')
df_target['날짜'] = pd.to_datetime(df_target['날짜'], errors='coerce').dt.strftime('%Y-%m-%d')

# 참조용 데이터 준비
ref_map = df_ref[['발전기명', '날짜', '일별_총_일사량(SI_Sum)']].copy()

# 병합 수행
df_updated = pd.merge(df_target, ref_map, on=['발전기명', '날짜'], how='left')

# 값 교체: 참조값이 존재하면 '합계 일사량(MJ/m2)'을 교체
mask = df_updated['일별_총_일사량(SI_Sum)'].notna()
df_updated.loc[mask, '합계 일사량(MJ/m2)'] = df_updated.loc[mask, '일별_총_일사량(SI_Sum)']

# 불필요한 참조 컬럼 제거
df_updated.drop(columns=['일별_총_일사량(SI_Sum)'], inplace=True)

# CSV로 저장
df_updated.to_csv(output_path, index=False, encoding= 'utf-8-sig')

print("✅ 일사량 값 교체 완료!")
print(f"저장 위치: {output_path}")
