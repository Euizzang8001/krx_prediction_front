import streamlit as st
from core.config import settings
from core.function import load_prediction_data, get_news_data, load_history_data, load_more_news
import requests
import pandas as pd
import plotly.graph_objects as go

# 웹페이지의 전체 너비를 사용하도록 설정
st.set_page_config(layout="wide")

# 반도체 관련 종목들의 이름과 종목 코드, 그래프 색 2개를 dict로 정의
stock_info = {
    "삼성전자": ["005930", "#1E90FF", "#FFA500"],
    "SK하이닉스": ["000660", "#FF0000", "#32CD32"],
    "한미반도체": ["042700", "#4169E1", "#FFD700"],
    "리노공업": ["058470", "#008080", "#FF4500"],
    "젬백스": ["082270", "#228B22", "#DAA520"],
    "HPSP": ["403870", "#6A5ACD", "#FF7F50"],
    "DB하이텍": ["000990", "#191970", "#FF6347"],
    "이오테크닉스": ["039030", "#4682B4", "#B8860B"],
    "주성엔지니어링": ["036930", "#006400", "#FF8C00"],
    "원익IPS": ["240810", "#0000CD", "#FFDAB9"]
}
server_url = settings.SERVER_URL  # 서버 URL 설정

#제목부분
st.title('🖥️반도체 종목 종가 예측')
st.write("반도체 관련 종목들의 종가 변화와 모델의 예측값을 확인해보세요.")
st.write("문의, 버그, 평가 :qkrdmlcks55@korea.ac.kr로 메일 보내주세요😁")
st.markdown("---")

#사이드바(종목 선택) 부분
st.sidebar.header("종목 선택")
#select box로 선택되도록 함
selected_stock_name = st.sidebar.selectbox(
    "보고 싶은 종목을 선택하세요:",
    list(stock_info.keys())
)

# 선택된 종목의 코드 가져와 화면에 나타내기
selected_stock_code = stock_info[selected_stock_name][0]
st.write(f"현재 선택된 종목: **{selected_stock_name} ({selected_stock_code})**")

#선택된 종목의 최근 종가, 예측 종가 변화율, 예측 종가 나타내는 부분
st.markdown(f"### 🔍 최근 {selected_stock_name} 종가, 예측 종가 변화율, 예측 종가")
# 서버로부터 데이터 가져오기
krx_prediction_data = load_prediction_data(selected_stock_name)
#가져온 데이터가 있다면 화면에 나타내기
if krx_prediction_data:
    data = {
        "항목": ["종가", "예측 종가 변화율", "예측 종가"],
        "값": [
            str(round(krx_prediction_data.get("closing"),2)) + "원",
            str(round(krx_prediction_data.get("predicted_closing_ratio") * 100,2)) + "%",
            str(round(krx_prediction_data.get("predicted_closing"), 2)) + "원"
        ]
    }
    #pandas dataframe으로 변환
    df = pd.DataFrame(data)

    #셀 텍스트 중앙 정렬하기
    new_df = df.set_index('항목').T.style.set_properties(**{'text-align': 'center'})

    #표 중앙 정렬하기
    col1, col2, col3 = st.columns([2, 2, 2])
    with col2:
        st.dataframe(new_df, use_container_width=True)

#예측 데이터가 없다면 오류 문구 띄우기
else:
    st.info(f"{selected_stock_name}의 예측 데이터를 불러올 수 없습니다.")

#### 종가 및 예측 종가 history
st.markdown("---")
st.write(f"### {selected_stock_name} 종가 및 예측 종가 트렌드")

#서버로부터 종가와 예측 종가 history 가져오기
history_data = load_history_data(selected_stock_name)

#history 데이터를 잘 받았다면 df로 나타내고 그래프로 나타내기
if history_data and history_data.get('date_list') and history_data.get('closing_list') and history_data.get(
        'predicted_closing_list'):
    #df로 변환
    history_df = pd.DataFrame({
        '날짜': pd.to_datetime(history_data['date_list']),
        '종가': history_data['closing_list'],
        '예측 종가': history_data['predicted_closing_list']
    })

    #한글로 column 변환
    history_df_melted = history_df.melt(id_vars=['날짜'], value_vars=['종가', '예측 종가'], var_name='구분', value_name='값')

    #그래프 항목 선언
    fig = go.Figure()

    # 종가 그래프 추가
    fig.add_trace(
        go.Scatter(
            x=history_df_melted[history_df_melted['구분'] == '종가']['날짜'],
            y=history_df_melted[history_df_melted['구분'] == '종가']['값'],
            mode='lines',
            name='종가',
            line=dict(color=stock_info[selected_stock_name][1])
        )
    )

    # 예측 종가 그래프 추가
    fig.add_trace(
        go.Scatter(
            x=history_df_melted[history_df_melted['구분'] == '예측 종가']['날짜'],
            y=history_df_melted[history_df_melted['구분'] == '예측 종가']['값'],
            mode='lines',
            name='예측 종가',
            line=dict(color=stock_info[selected_stock_name][2])
        )
    )

    # 그래프 설정 업데이트
    fig.update_layout(
        title=f"{selected_stock_name} 종가 및 예측 종가 변화",
        xaxis_title='날짜',
        yaxis_title='가격',
        legend_title='데이터 종류',
        hovermode='x unified',
        height=400
    )

    # X축은 숨기기
    fig.update_xaxes(
        visible=False,
        showgrid=False
    )

    # 날짜 및 가격 포멧 설정
    fig.update_traces(
        hovertemplate="날짜: %{x|%Y-%m-%d}<br>값: %{y:.0f}원<extra></extra>"
    )
    # 그래프 그리기
    st.plotly_chart(fig, use_container_width=True)

#불러온 데이터가 없다면 오류 문구 띄우기
else:
    st.info(f"{selected_stock_name}의 과거 데이터를 불러올 수 없습니다.")



##### 뉴스 부분

#cursor와 news들을 session_state에서 관리하여 뉴스를 계속 업로드할 수 있도록 함
if 'cursor' not in st.session_state:
    st.session_state.cursor = 0
if 'news_data' not in st.session_state:
    st.session_state.news_data = []

st.markdown("---")
st.markdown("### 📰 실시간 반도체 종목 관련 뉴스")

# 페이지 로드 시 뉴스가 없다면 뉴스 첫 로드하기
if not st.session_state.news_data:
    load_more_news()

#뉴스가 존재한다면, 뉴스를 화면에 나타내기
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
#뉴스가 없다면, 에러 메세지 띄우기
else:
    st.info("현재 표시할 뉴스가 없습니다.")


#버튼을 화면의 가운데에 오도록 markdown
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

# 뉴스 더보기 버튼을 누르면, 뉴스를 더 불러오고 rerun
if st.button("반도체 관련 최신 뉴스 더보기", key="load_more_news_button"):
    load_more_news()
    st.rerun()