import streamlit as st
from file_service import get_available_dates, get_users_for_date
from utils import format_date


def display_sidebar():
    # 사용 가능한 날짜 목록 가져오기
    available_dates = get_available_dates()
    selected_user = None  # 선택된 사용자 저장
    selected_date = None  # 선택된 날짜 저장
    selected_user_id = None
    

    for date in available_dates:
        formatted_date = format_date(date)  # 날짜 형식 변환
        with st.sidebar.expander(f"{formatted_date}", expanded=False):
            users = get_users_for_date(date)
            if users:
                for user in users:
                    username = user['username']
                    user_id = user['id']
                    # 고유한 key 값을 생성합니다
                    key = f"user_button_{user_id}_{username}_{formatted_date}"
                    if st.button(username, key=key, use_container_width=True):
                        selected_user = username  # 선택된 사용자 이름 저장
                        selected_user_id = user_id  # 선택된 사용자 ID 저장
                        selected_date = formatted_date  # 선택된 날짜 저장
            else:
                st.write("사용자가 없습니다.")
    
    return selected_user, selected_date, selected_user_id
