import streamlit as st
from core.config import settings
import requests

if 'cursor' not in st.session_state:
    st.session_state.cursor = 0
if 'news_data' not in st.session_state:
    st.session_state.news_data = []

st.title('🖥️반도체 종목 종가 예측')
st.write(
    "반도체 관련 종목들의 종가 변화와 모델의 예측값을 확인해보세요."
)

st.markdown("### 🔍 종목 검색 안내")
st.write(
    "보고 싶은 종목을 선택하거나 검색하여 왼쪽 탭에서 확인해보세요. "
)
st.write(
    "예측된 종가와 다양한 지표들을 함께 확인할 수 있습니다."
)

# 메인 화면 콘텐츠
st.markdown("### 📰 실시간 반도체 종목 관련 뉴스")

server_url = settings.SERVER_URL

def load_more_news():
    response = requests.get(server_url + f'api/v1/news/{st.session_state.cursor}')
    if response.status_code == 200:
        new_news_list = response.json()
        st.session_state.news_data.extend(new_news_list)
        st.session_state.cursor += len(new_news_list)

        if not new_news_list:
            st.info("더 이상 새로운 뉴스가 없습니다.")
            return False
    else:
        st.error(f"뉴스를 불러오는 데 실패했습니다: {response.status_code}")
        return False
    return True

if not st.session_state.news_data:
    load_more_news()

if st.session_state.news_data:
    for news in st.session_state.news_data:
        st.markdown(
            f"""
            <div style="border:1px solid #ddd; padding:10px; border-radius:10px; margin-bottom:10px">
                <a href="{news['link']}" target="_blank" style="text-decoration: none;">
                    <h4 style="font-size: 20px; color: #1f77b4;">{news['title']}</h4>
                    <p style="font-size: 15px; color: #555;">{news['description']}</p>
                    <p style="font-size: 13px; color: gray;">원본 링크: {news['link']} | 출간 시간: {news['pub_time']}</p>
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )
else:
    st.info("현재 표시할 뉴스가 없습니다.")

st.markdown(
    """
    <style>
    .stButton > button {
        display: block;
        margin: 0 auto; 
    }
    </style>
    """,
    unsafe_allow_html=True
)


if st.button("반도체 관련 최신 뉴스 더보기", key="load_more_news_button"):
    load_more_news()
    st.rerun()