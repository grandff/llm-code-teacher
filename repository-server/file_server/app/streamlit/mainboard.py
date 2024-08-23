import pandas as pd
import streamlit as st
from file_service import get_files_for_date
import logging


# 상수 정의
DOWNLOAD_CHECK_COLUMN = "다운로드 체크"
FILE_NAME_COLUMN = "파일이름"
CREATED_AT_COLUMN = "생성시간"
FILE_PATH_COLUMN = "다운로드 링크"


# 로그 설정
logger = logging.getLogger(__name__)

# 페이지 설정
#st.set_page_config(layout="wide")  # 페이지 레이아웃을 넓게 설정
def display_mainboard(selected_date, selected_user,selected_user_id):

    # 선택한 날짜에 대한 파일 리스트 가져오기
    files = get_files_for_date(selected_date, selected_user_id)
    if files:
        data = []
        #for id, user_id, file_name, file_path, created_at in files:
        for file in files:
            file_name = file.get('file_name')
            file_path = file.get('file_path')
            created_at = file.get('created_at')
            # URL 경로 생성
            file_url = f"http://localhost:9501/download/{file_path}"
            
            data.append({
                FILE_NAME_COLUMN: file_name,
                CREATED_AT_COLUMN: created_at,
                FILE_PATH_COLUMN: file_url,
                DOWNLOAD_CHECK_COLUMN: False
            })
        
        # DataFrame 생성
        data_df = pd.DataFrame(data)

        # 데이터프레임 표시
        st.dataframe(
            data_df,
            column_config={
                DOWNLOAD_CHECK_COLUMN: st.column_config.CheckboxColumn(help="Want download check"),
                FILE_PATH_COLUMN: st.column_config.LinkColumn(help="File download link"),
            }
        )

    else:
        st.write("해당 날짜에 파일이 없습니다.")
        data_df = pd.DataFrame(columns=[FILE_NAME_COLUMN, CREATED_AT_COLUMN, FILE_PATH_COLUMN, DOWNLOAD_CHECK_COLUMN])
        st.dataframe(data_df)

    # 사용자 세션 저장
    st.session_state.selected_user = selected_user
    st.session_state.selected_date = selected_date
    st.session_state.selected_user_id = selected_user_id