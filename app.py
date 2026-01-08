import streamlit as st
import pandas as pd
import time
import random
import os
import plotly.express as px
from datetime import datetime
import plotly.io as pio

# --- 설정 및 디자인 (이 부분이 있으면 따로 파일을 안 만들어도 됩니다) ---
st.set_page_config(page_title="Neuro-Focus Lab", page_icon="🧠", layout="wide")
pio.templates.default = "plotly_dark"

# 검은색 테마를 강제로 적용하는 스타일 코드
st.markdown("""
    <style>
    /* 전체 배경을 어둡게 */
    .stApp {
        background-color: #222831;
        color: #EEEEEE;
    }
    /* 사이드바 배경 */
    [data-testid="stSidebar"] {
        background-color: #393E46;
    }
    /* 버튼 스타일 */
    .stButton>button {
        color: #EEEEEE;
        background-color: #393E46;
        border: 2px solid #00ADB5;
        border-radius: 8px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #00ADB5;
        color: white;
    }
    /* 큰 글씨 색상 */
    h1, h2, h3 {
        color: #00ADB5 !important;
    }
    /* 입력창 글씨 */
    .stTextInput > div > div > input {
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 기능 시작 ---
DATA_FILE = "neuro_data.csv"

# 데이터 파일 없으면 생성
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Timestamp", "Test_Type", "Score", "Sleep_Hours", "Caffeine", "Condition"])
    df.to_csv(DATA_FILE, index=False)

def save_record(test_type, score, sleep, caffeine, condition):
    new_data = pd.DataFrame({
        "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M")],
        "Test_Type": [test_type],
        "Score": [score],
        "Sleep_Hours": [sleep],
        "Caffeine": [caffeine],
        "Condition": [condition]
    })
    new_data.to_csv(DATA_FILE, mode='a', header=False, index=False)
    st.success(f"✅ {test_type} 결과 저장 완료!")

# --- 사이드바 ---
with st.sidebar:
    st.title("🧪 연구 설정")
    user_sleep = st.slider("수면 시간", 0, 12, 7)
    user_caffeine = st.radio("카페인 섭취", ["X", "O"])
    user_condition = st.select_slider("컨디션", options=["나쁨", "보통", "좋음"])

menu = st.sidebar.radio("메뉴", ["🏠 홈", "🎨 스트룹 테스트", "🔢 숫자 기억력", "⚡ 반응 속도", "📊 데이터 분석"])

# --- 메인 화면 ---
if menu == "🏠 홈":
    st.title("🧠 Neuro-Focus Lab")
    st.write("왼쪽 메뉴에서 실험을 선택하세요.")

elif menu == "🎨 스트룹 테스트":
    st.title("🎨 스트룹 테스트")
    st.info("글자의 '색깔'을 맞추세요!")
    if 'stroop_score' not in st.session_state: st.session_state.stroop_score = 0
    
    colors = {'빨강': '#FF4B4B', '파랑': '#1E90FF', '초록': '#00C897'}
    words = list(colors.keys())

    col1, col2 = st.columns(2)
    with col1:
        if st.button("문제 시작/다음"):
            st.session_state.word = random.choice(words)
            st.session_state.color_key = random.choice(words)
            st.session_state.color_val = colors[st.session_state.color_key]
    
    if 'word' in st.session_state:
        st.markdown(f"<h1 style='color:{st.session_state.color_val}; font-size:60px;'>{st.session_state.word}</h1>", unsafe_allow_html=True)
        cols = st.columns(3)
        for i, (txt, code) in enumerate(colors.items()):
            if cols[i].button(txt):
                if txt == st.session_state.color_key:
                    st.success("정답!")
                    st.session_state.stroop_score += 1
                    save_record("Stroop", st.session_state.stroop_score, user_sleep, user_caffeine, user_condition)
                else:
                    st.error("오답!")

elif menu == "🔢 숫자 기억력":
    st.title("🔢 숫자 기억력")
    if st.button("문제 보기"):
        nums = "".join([str(random.randint(0,9)) for _ in range(5)]) # 5자리 예시
        st.session_state.quiz_nums = nums
        msg = st.empty()
        msg.header(f"기억하세요: {nums}")
        time.sleep(2)
        msg.empty()
    
    ans = st.text_input("숫자 입력")
    if st.button("제출"):
        if 'quiz_nums' in st.session_state and ans == st.session_state.quiz_nums:
            st.success("성공!")
            save_record("DigitSpan", 100, user_sleep, user_caffeine, user_condition)
        else:
            st.error("실패!")

elif menu == "⚡ 반응 속도":
    st.title("⚡ 반응 속도")
    if st.button("시작"):
        st.write("준비...")
        time.sleep(random.randint(2,4))
        st.session_state.start = time.time()
        st.error("지금 클릭하세요!!! (아래 버튼)")
    
    if st.button("클릭!"):
        if 'start' in st.session_state:
            sec = time.time() - st.session_state.start
            st.success(f"{sec:.3f}초")
            save_record("Reaction", sec, user_sleep, user_caffeine, user_condition)

elif menu == "📊 데이터 분석":
    st.title("📊 데이터 분석")
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        st.dataframe(df)
        fig = px.bar(df, x="Condition", y="Score", color="Test_Type", title="컨디션별 점수")
        st.plotly_chart(fig)
    else:
        st.write("데이터가 없습니다.")