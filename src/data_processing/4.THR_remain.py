import os
import sys
import pandas as pd

# -----------------------------
# 설정: 경로만 바꿔서 사용하세요
# -----------------------------
input_path  = "/Users/parkhyeji/Desktop/PV/data/outliers_removed/이상치제거_데이터.csv"   # CSV 또는 XLSX 가능
output_path = "/Users/parkhyeji/Desktop/PV/data/outliers_removed/이상치제거_THR.csv"  # 확장자에 맞춰 저장됨

# 최종으로 남길 열(순서 포함)
TARGET_COLS = [
    "지점",
    "날짜",
    "발전기명",
    "설비용량(MW)",
    "발전량(MWh)",
    "평균기온(°C)",
    "평균 상대습도(%)",
    "합계 일사량(MJ/m2)",
]

# 열 이름 정리용(공백/탭 제거, 'Unnamed' 제거 등)
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # 앞뒤 공백/탭 제거
    df.columns = df.columns.astype(str).str.replace(r"\s+", "", regex=True)
    # 흔한 변형을 표준화하기 위한 매핑(필요시 추가)
    std_map = {
        # 공백 제거 전제이므로 키도 공백없음
        "평균풍속(m/s)": "평균 풍속(m/s)",
        "평균상대습도(%)": "평균 상대습도(%)",
        "합계일조시간(hr)": "합계 일조시간(hr)",
        "합계일사량(MJ/m2)": "합계 일사량(MJ/m2)",
        "설비용량(MW)": "설비용량(MW)",
        "발전량(MWh)": "발전량(MWh)",
        "평균기온(°C)": "평균기온(°C)",
    }

    # 표준화 적용을 위해 한 번 원본도 보유
    original_cols = df.columns.tolist()
    new_cols = []
    for c in original_cols:
        # 'Unnamed' 열 제거용 표시를 위해 우선 원본 문자로 유지
        orig = c
        # 다시 보기 좋게: 중간에 공백 되살리기 위해 표준 키와 매칭
        key = c  # 공백 제거된 상태
        mapped = std_map.get(key, None)

        # 사람이 읽기 좋은 최종 이름 선택
        if mapped:
            new_cols.append(mapped)
        else:
            # 숫자/문자 그대로 사용하되, 'Unnamed'는 제거 대상 표시
            if "Unnamed" in orig or orig.strip() == "":
                new_cols.append(f"__DROP__{orig}")
            else:
                # 공백 제거했던 걸 원상복구할 수 없으니 원래 이름 사용
                new_cols.append(orig)

    df.columns = new_cols
    # Unnamed 등 버릴 열 제거
    drop_cols = [c for c in df.columns if c.startswith("__DROP__")]
    if drop_cols:
        df = df.drop(columns=drop_cols, errors="ignore")

    # 열 이름 앞뒤 공백 최종 정리
    df.columns = df.columns.str.strip()
    return df

def read_any(input_path: str) -> pd.DataFrame:
    ext = os.path.splitext(input_path)[1].lower()
    if ext in [".csv", ".txt"]:
        # 인코딩 자동 시도
        for enc in ["utf-8-sig", "cp949", "utf-8"]:
            try:
                return pd.read_csv(input_path, encoding=enc)
            except Exception:
                continue
        # 그래도 실패하면 기본 시도(에러 표시)
        return pd.read_csv(input_path)
    elif ext in [".xlsx", ".xls"]:
        return pd.read_excel(input_path)
    else:
        raise ValueError("지원하지 않는 파일 형식입니다. CSV 또는 XLSX를 사용하세요.")

def write_any(df: pd.DataFrame, output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    ext = os.path.splitext(output_path)[1].lower()
    if ext in [".csv", ".txt"]:
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
    elif ext in [".xlsx", ".xls"]:
        df.to_excel(output_path, index=False)
    else:
        # 확장자 없거나 이상하면 CSV로 저장
        fallback = output_path + ".csv"
        print(f"[경고] 알 수 없는 확장자라 CSV로 저장합니다 → {fallback}")
        df.to_csv(fallback, index=False, encoding="utf-8-sig")

def main():
    # 1) 읽기
    try:
        df = read_any(input_path)
    except Exception as e:
        print(f"[에러] 파일을 읽는 중 문제가 발생했습니다: {e}")
        sys.exit(1)

    # 2) 열 정리
    df = normalize_columns(df)

    # 3) 대상 열 존재 확인 및 선택
    #    여기서 TARGET_COLS와 현재 df.columns의 공백 차이를 줄이기 위해 둘 다 strip 처리
    target_clean = [c.strip() for c in TARGET_COLS]
    current_cols_clean = [c.strip() for c in df.columns]

    missing = [c for c in target_clean if c not in current_cols_clean]
    if missing:
        print("[경고] 다음 열을 찾지 못했습니다(파일에 없거나 이름이 다른 듯 합니다):")
        for m in missing:
            print("  -", m)
        # 꼭 필요한 핵심 열이 빠졌는지 확인(날짜, 발전기명, 발전량 등)
        must_have = {"지점", "날짜", "발전기명", "발전량(MWh)"}
        if any(m in must_have for m in missing):
            print("\n[중단] 핵심 열이 누락되어 재구성할 수 없습니다. 파일의 열 이름을 확인하세요.")
            print("현재 열 목록:", list(df.columns))
            sys.exit(1)

    # 선택 가능한 열만 추출 (순서 유지)
    final_cols = [c for c in TARGET_COLS if c.strip() in current_cols_clean]
    df_out = df[final_cols].copy()

    # 4) 저장
    try:
        write_any(df_out, output_path)
    except Exception as e:
        print(f"[에러] 파일 저장 중 문제가 발생했습니다: {e}")
        sys.exit(1)

    # 5) 보고
    print("✅ 열 재구성 완료!")
    print(" - 입력 파일:", input_path)
    print(" - 출력 파일:", output_path)
    print(" - 최종 열 순서:", list(df_out.columns))

if __name__ == "__main__":
    main()
