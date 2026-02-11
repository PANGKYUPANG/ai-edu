import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# 1. 페이지 설정 (Page Setup)
st.set_page_config(layout="wide", page_title="일일 재고 현황표")
st.title("🏭 일일 재고 현황표 (Daily Inventory Status)")

# 2. 데이터 로드 (Load Data)
# 대리님이 공유해주신 구글 시트 URL을 CSV 내보내기 링크로 변환하여 읽어옵니다.
# 별도의 인증 키 없이 공개된 시트를 읽을 수 있는 가장 쉬운 방법입니다.
sheet_id = "1Jhfr4-e5CWJHVQ8nAQCOaZdkn2BYz5ZnMnO53vxia08"
csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

@st.cache_data(ttl=60) # 60초마다 데이터 갱신
def load_data():
    try:
        # CSV로 읽어오기
        df = pd.read_csv(csv_url)
        # 공백 제거 등 전처리
        df.columns = [c.strip() for c in df.columns]
        # 검색하기 쉽도록 사일로 이름을 인덱스로 설정 (문자열로 변환하여 매칭)
        data_dict = {}
        for _, row in df.iterrows():
            silo_name = str(row['장치장']).strip().lower() # 소문자로 통일하여 매칭
            data_dict[silo_name] = {
                'item': str(row['곡종']),
                'qty': str(row['재고량'])
            }
        return data_dict
    except Exception as e:
        st.error(f"데이터를 불러오는데 실패했습니다: {e}")
        return {}

inventory_data = load_data()

# 3. 시각화 그리기 (Visualization)
def draw_silo_map(data):
    fig, ax = plt.subplots(figsize=(15, 8))
    ax.set_aspect('equal')
    ax.axis('off') # 축 숨기기

    # 좌표계 설정 (Logic)
    # Y축: 100계열(Top)=4, 300계열(Mid)=2, 500계열(Bot)=0
    # X축: 원형 사일로는 2, 4, 6, 8, 10, 12 위치에 배치
    # 사이공간(200, 400)은 Y축 3, 1 위치. X축은 1, 3, 5... 등 홀수 위치
    
    # 도형 그리기 함수
    def add_silo(name, x, y, shape, label_y_offset=0):
        # 데이터 매칭 (대소문자 구분 없이)
        key = name.lower()
        info = data.get(key, {'item': '-', 'qty': '0'})
        
        # 도형 모양 결정
        if shape == 'circle':
            # 원형 (100, 300, 500 계열)
            color = '#a8dadc' # 하늘색
            patch = plt.Circle((x, y), 0.9, color=color, ec='black')
        elif shape == 'star':
            # 별모양 (내부 사이 공간)
            color = '#f1faee' # 흰색에 가까운 색
            # 마름모꼴로 표현
            patch = patches.RegularPolygon((x, y), numVertices=4, radius=0.8, color=color, ec='black')
        elif shape == 'half_left':
            # 왼쪽 반-별 (A201, A401) - 오른쪽을 가리키는 삼각형
            color = '#e63946' # 붉은색 포인트
            patch = patches.RegularPolygon((x, y), numVertices=3, radius=0.7, orientation=0, color=color, ec='black') 
            # orientation 0은 보통 오른쪽을 봄 (matplotlib 버전에 따라 다를 수 있음, 여기선 삼각형으로 대체)
        elif shape == 'half_right':
            # 오른쪽 반-별 (A207, A407) - 왼쪽을 가리키는 삼각형
            color = '#e63946'
            patch = patches.RegularPolygon((x, y), numVertices=3, radius=0.7, orientation=3.14, color=color, ec='black')

        ax.add_patch(patch)
        
        # 텍스트 라벨 (이름, 품목, 수량)
        label_text = f"{name}\n{info['item']}\n{info['qty']}"
        ax.text(x, y + label_y_offset, label_text, ha='center', va='center', fontsize=9, fontweight='bold', color='#1d3557')

    # --- 1. 원형 사일로 배치 (18개) ---
    # 100계열 (Top, Y=4)
    for i in range(1, 7):
        add_silo(f"A10{i}", i*2, 4, 'circle')
    # 300계열 (Mid, Y=2)
    for i in range(1, 7):
        add_silo(f"A30{i}", i*2, 2, 'circle')
    # 500계열 (Bot, Y=0)
    for i in range(1, 7):
        add_silo(f"A50{i}", i*2, 0, 'circle')

    # --- 2. 별모양 사일로 배치 (10개) + 반-별 (4개) ---
    # 200계열 (Top Gap, Y=3)
    # A201 (Left Half) -> X=1
    add_silo("A201", 1, 3, 'half_left')
    # A202 ~ A206 (Stars) -> X=3, 5, 7, 9, 11
    for i in range(2, 7):
        add_silo(f"A20{i}", (i*2)-1, 3, 'star')
    # A207 (Right Half) -> X=13
    add_silo("A207", 13, 3, 'half_right')

    # 400계열 (Bot Gap, Y=1)
    # A401 (Left Half) -> X=1
    add_silo("A401", 1, 1, 'half_left')
    # A402 ~ A406 (Stars) -> X=3, 5, 7, 9, 11
    for i in range(2, 7):
        add_silo(f"A40{i}", (i*2)-1, 1, 'star')
    # A407 (Right Half) -> X=13
    add_silo("A407", 13, 1, 'half_right')

    # 그래프 범위 설정
    ax.set_xlim(0, 14)
    ax.set_ylim(-1, 5)
    
    st.pyplot(fig)

# 실행
if inventory_data:
    draw_silo_map(inventory_data)
else:
    st.warning("데이터를 불러오지 못했습니다. 구글 시트 URL 권한을 확인해주세요.")
