import pandas as pd
import geopandas as gpd   # 지도경계데이터 (GeoJSON) 사용 가능 도구
import folium # 지도 생성 도구 

# --- 1. 데이터 불러오기 ---

# (A) 지도 모양 데이터 불러오기
# 지도 파일을 읽어오기 ( 각 구의 이름과 경계선 좌표 정보)
seoul_gu_geo = gpd.read_file('gadm41_KOR_1.json')

# (B) 내가 사용할 데이터 불러오기
# './위치정보/' 폴더에 있는 CSV 파일을 읽어옵니다.
my_data = pd.read_csv('./위치정보/map_public.csv')
print("CSV 파일에서 읽어온 열 이름:", my_data.columns)


# --- 2. 두 데이터 합치기 ---

# 'name'(구 이름)을 기준으로 지도 모양과 내 데이터를 하나로 합칩니다.
seoul_gu_data = seoul_gu_geo.merge(my_data, on='name')


# --- 3. 인터랙티브 지도 만들기 ---

# (A) 서울 중심에 기본 지도 생성
m = folium.Map(location=[37.5665, 126.9780], zoom_start=11)

# (B) 데이터에 따라 구별로 색칠하기
# my_data의 'value' 컬럼을 기준으로 색을 칠합니다.
# 만약 'value'가 아니라 다른 컬럼 이름이라면 그 이름으로 바꿔주세요!
folium.Choropleth(  # 단계 구분도를 그리는 기능 
    geo_data=seoul_gu_data,
    data=seoul_gu_data,
    columns=['name', 'value'],
    key_on='feature.properties.name',
    fill_color='YlGnBu',
    legend_name='나의 데이터 값',
).add_to(m)

# (C) 마우스 올리면 정보 뜨게 하고, 클릭하면 팝업 띄우기
folium.GeoJson(
    seoul_gu_data,
    tooltip=folium.GeoJsonTooltip(
        fields=['name', 'value'],
        aliases=['구 이름:', '데이터 값:'],
        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
    ),
    popup=folium.GeoJsonPopup(
        fields=['name', 'value'],
        aliases=['구 이름', '데이터 값']
    )
).add_to(m)


# --- 4. 파일로 저장하기 ---

# RE_PV 폴더에 'seoul_interactive_map.html' 파일이 생성됩니다.
m.save('seoul_interactive_map.html')

print("지도 생성이 완료되었습니다! seoul_interactive_map.html 파일을 열어보세요. ✨")