import streamlit as st
from database import create_connection, get_files_for_date
from sidebar import display_sidebar
from mainboard import display_mainboard 


def main():
    
    #database 연결
    conn = create_connection()

    # 세션 상태 확인
    #st.write(f"세션: {st.session_state}")   
             
    if 'selected_user' not in st.session_state:
        st.session_state.selected_user = None
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = None
    if 'selected_user_id' not in st.session_state:
        st.session_state.selected_user_id = None



    # 사이드바에서 사용자와 날짜 선택시
    selected_user, selected_date, selected_user_id = display_sidebar(conn)
    if selected_user:
        st.session_state.selected_user = selected_user
    if selected_date:
        st.session_state.selected_date = selected_date
    if selected_user_id:
        st.session_state.selected_user_id = selected_user_id

    # 기존의 데이터가 존재하는 경우
    if 'selected_user' in st.session_state:
        selected_user = st.session_state.selected_user
    if 'selected_date' in st.session_state:
        selected_date = st.session_state.selected_date
    if 'selected_user_id' in st.session_state:
        selected_user_id = st.session_state.selected_user_id
    

    
    if selected_date and selected_user:
        st.header("파일 리스트")
        # 날짜 및 사용자 입력 필드
        selected_date = st.text_input("날짜 입력 (형식: YYYY-MM-DD)", "2024-08-13")
        selected_user = st.text_input("사용자 입력", "miyeonlim")

        st.markdown(
            f"<h4>날짜: {selected_date} 사용자: {selected_user}</h4>",
            unsafe_allow_html=True
        )
        st.write("---------------------------------------------------------------")

        # mainboard 내용 표시
        display_mainboard(conn, selected_date, selected_user, selected_user_id)

    conn.close()
    

if __name__ == "__main__":
    main()