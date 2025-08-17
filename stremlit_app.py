import streamlit as st
import pandas as pd

st.set_page_config(page_title="⚓ 길드 함선 제작 재료 현황", layout="wide")

# -------------------------------
# 필요 재료 데이터 구조
# -------------------------------
materials = {
    "1차재료": {
        "목재+": 1000,
        "상급목재": 1000,
        "타르": {"수량": 200, "레시피": {"통나무": 50, "점토": 25}}
    },
    "2차재료": {
        "강철괴": 1500,
        "목재+": 2000,
        "아교": {"수량": 250, "레시피": {"상급생가죽": 30, "물이든병": 10}}
    }
}

# -------------------------------
# 초기 세션 상태 (길드원 데이터)
# -------------------------------
if "guild_data" not in st.session_state:
    st.session_state.guild_data = {}  # {닉네임: {재료명: 수량, ...}}

# -------------------------------
# 닉네임 입력 및 보유 자원 입력
# -------------------------------
st.sidebar.header("길드원 자원 입력")

nickname = st.sidebar.text_input("닉네임을 입력하세요")

if nickname:
    prev_data = st.session_state.guild_data.get(nickname, {})

    st.sidebar.subheader("보유 자원 입력")

    input_data = {}
    base_materials = ["목재+", "상급목재", "통나무", "점토", "강철괴", "상급생가죽", "물이든병"]

    for mat in base_materials:
        input_data[mat] = st.sidebar.number_input(
            f"{mat} 보유 수량", 
            min_value=0, 
            value=prev_data.get(mat, 0), 
            step=10
        )

    if st.sidebar.button("저장/업데이트"):
        st.session_state.guild_data[nickname] = input_data
        st.success(f"{nickname} 님의 자원 정보가 저장되었습니다!")

# -------------------------------
# 전체 집계 (길드원 합산)
# -------------------------------
df = pd.DataFrame(st.session_state.guild_data).T.fillna(0).astype(int)
total = df.sum().to_dict() if not df.empty else {}

# -------------------------------
# 화면 출력
# -------------------------------
st.header("📦 길드 함선 제작 재료 현황")

col1, col2 = st.columns(2)

def render_progress(label, need, have, img_url=None):
    percent = min(have / need, 1.0) if need > 0 else 1
    if img_url:
        st.image(img_url, width=40)
    st.write(f"**{label}**: {have}/{need} (부족 {max(0, need-have)})")
    st.progress(percent)

# 1차 재료
with col1:
    st.subheader("🪵 1차 재료")
    for mat, val in materials["1차재료"].items():
        if isinstance(val, dict):  # 타르
            need = val["수량"]
            recipe_need = {k: v*need for k, v in val["레시피"].items()}
            have = min(total.get(k, 0)//v for k, v in val["레시피"].items()) if total else 0
            render_progress(mat, need, have)
            st.caption(f"({recipe_need}) 필요")
        else:
            have = total.get(mat, 0)
            render_progress(mat, val, have)

# 2차 재료
with col2:
    st.subheader("⚒️ 2차 재료")
    for mat, val in materials["2차재료"].items():
        if isinstance(val, dict):  # 아교
            need = val["수량"]
            recipe_need = {k: v*need for k, v in val["레시피"].items()}
            have = min(total.get(k, 0)//v for k, v in val["레시피"].items()) if total else 0
            render_progress(mat, need, have)
            st.caption(f"({recipe_need}) 필요")
        else:
            have = total.get(mat, 0)
            render_progress(mat, val, have)

# -------------------------------
# 길드원별 입력 현황 테이블
# -------------------------------
st.subheader("👥 길드원별 입력 현황")
if not df.empty:
    st.dataframe(df)
else:
    st.info("아직 입력된 자원이 없습니다.")
