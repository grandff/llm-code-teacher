import streamlit as st
from database import get_available_dates, get_users_for_date
from utils import format_date


def display_sidebar(conn):
    # 사용 가능한 날짜 목록 가져오기
    available_dates = get_available_dates(conn)
    selected_user = None  # 선택된 사용자 저장
    selected_date = None  # 선택된 날짜 저장
    selected_user_id = None
    

    # 날짜를 메뉴 항목으로 추가
    for i, date in enumerate(available_dates, start=1):
        formatted_date = format_date(date)  # 날짜 형식 변환
        with st.sidebar.expander(f"{formatted_date}", expanded=False):
            users = get_users_for_date(conn, date)
            if users:
                for username, user_id in users:
                   if st.button(username, key=f"user_button_{i}_{username}", use_container_width=True):
                        selected_user = username  # 선택된 사용자 이름 저장
                        selected_user_id = user_id  # 선택된 사용자 ID 저장
                        selected_date = formatted_date  # 선택된 날짜 저장
            else:
                st.write("사용자가 없습니다.")
    
    return selected_user, selected_date, selected_user_id
