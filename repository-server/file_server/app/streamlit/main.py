import os
import logging
import logging.config
import json
import streamlit as st
from sidebar import display_sidebar
from mainboard import display_mainboard 


# JSON 파일 경로
logging_config_file = os.path.join(os.path.dirname(__file__), 'config', 'logging_config.json')

# JSON 파일에서 로그 설정 읽기
if os.path.exists(logging_config_file):
    with open(logging_config_file, 'r') as f:
        config = json.load(f)
        logging.config.dictConfig(config)
else:
    logging.basicConfig(level=logging.INFO)
    print(f"Warning: 로그 설정 파일을 찾을 수 없습니다. 기본 설정으로 시작합니다.")

# logger 설정
logger = logging.getLogger("my_logger")

def main():
    st.set_page_config(layout="wide")

    # 세션 상태 확인
    #st.write(f"세션: {st.session_state}")   
             
    if 'selected_user' not in st.session_state:
        st.session_state.selected_user = None
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = None
    if 'selected_user_id' not in st.session_state:
        st.session_state.selected_user_id = None

    # 사이드바에서 사용자와 날짜 선택시
    selected_user, selected_date, selected_user_id = display_sidebar()
    if selected_user:
        st.session_state.selected_user = selected_user
    if selected_date:
        st.session_state.selected_date = selected_date
    if selected_user_id:
        st.session_state.selected_user_id = selected_user_id

    # 기존의 데이터가 존재하는 경우
    selected_user = st.session_state.selected_user
    selected_date = st.session_state.selected_date
    selected_user_id = st.session_state.selected_user_id
    

    
    if selected_date and selected_user:
        st.header("파일 리스트")
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <h5 style="margin: 0; font-size: 14px;">날짜 : <span style="color: #3498DB;">{selected_date}</span></h5>
                <h5 style="margin: 0; font-size: 14px; margin-left: 5px;">사용자 : <span style="color: #3498DB;">{selected_user}</span></h5>
            </div>
            <hr style="border: 1px solid #ccc; margin-top: 2px;">
            """,
            unsafe_allow_html=True
        )
        
        # mainboard 내용 표시
        display_mainboard(selected_date, selected_user, selected_user_id)


if __name__ == "__main__":
    main()