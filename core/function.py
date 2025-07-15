import streamlit as st
from core.config import settings
import requests
import pandas as pd

server_url = settings.SERVER_URL

#종목 이름으로 종가, 예측 종가 변화율, 예측 종가를 불러오는 함수 선언
@st.cache_data(ttl=3600) #1시간동안 해당 함수 결과를 캐시로 저장
def load_prediction_data(stock_name):
    try:
        response = requests.get(server_url + f"/api/v1/krx_prediction/{stock_name}")
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생시키기
        return response.json() #json 형태로 return
    # 만약 예외가 발생했다면, 예외 문구 띄우기
    except requests.exceptions.RequestException as e:
        st.error(f"예측 데이터를 불러오는 데 실패했습니다: {e}")
        return None

#종목 이름으로 현재까지의 종가, 예측 종가를 불러오는 함수
@st.cache_data(ttl=3600) #1시간동안 해당 함수 결과를 캐시로 저장
def load_history_data(stock_name):
    #서버에 request하여 그 결과를 json으로 변환 후 return
    try:
        response = requests.get(server_url + f"/api/v1/krx_closing/{stock_name}")
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        return response.json()
    #예외가 발생했다면, 예외 문구 띄우기
    except requests.exceptions.RequestException as e:
        st.error(f"과거 데이터를 불러오는 데 실패했습니다: {e}")
        return None

#cursor를 기준으로 다음 5개의 뉴스를 return하는 함수
@st.cache_data(ttl=3600) #뉴스는 1시간마다 refresh되게끔 함
def get_news_data(current_cursor):
    #현재 cursor값 이후의 5개의 뉴스를 가져오기
    try:
        response = requests.get(server_url + f'api/v1/news/{current_cursor}')
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        return response.json()
    #예외가 발생했다면, 예외 문구 띄우기
    except requests.exceptions.RequestException as e:
        st.error(f"뉴스를 불러오는 데 실패했습니다: {e}")
        return []

# 현재 cursor값을 기준으로, cursor 이후의 뉴스를 가져와 보여지는 뉴스를 추가하는 함수
def load_more_news():
    new_news_list = get_news_data(st.session_state.cursor) #현재 커서를 기준으로 뉴스 가져오기
    if new_news_list: #더 추가할 뉴스가 있다면 뉴스 list를 확장하고, session_state에 있는 커서 늘려주기
        st.session_state.news_data.extend(new_news_list)
        st.session_state.cursor += len(new_news_list)
    #더 추가할 뉴스가 없다면 새로운 뉴스가 없음을 알리는 문구 띄우기
    else:
        st.info("더 이상 새로운 뉴스가 없습니다.")
        return False
    return True