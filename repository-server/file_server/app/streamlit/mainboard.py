import pandas as pd
import streamlit as st
from file_service import get_files_for_date
from filePreview_service import preview_file  # 파일 미리보기 서비스 불러오기
import logging
from datetime import datetime

# 상수 정의
DOWNLOAD_CHECK_COLUMN = "다운로드 체크"
FILE_NAME_COLUMN = "파일이름"
CREATED_AT_COLUMN = "생성시간"
FILE_PATH_COLUMN = "다운로드 링크"
PREVIEW_COLUMN = "미리보기"  # 미리보기 버튼 열 추가

# 로그 설정
logger = logging.getLogger("my_logger")

def display_mainboard(selected_date, selected_user, selected_user_id):
    # 선택한 날짜에 대한 파일 리스트 가져오기
    files = get_files_for_date(selected_date, selected_user_id)
    if files:
        data = []
        preview_button_image_url = "https://img.icons8.com/ios-filled/50/808080/document--v1.png"

        #for file in enumerate(files):
        for file in files:    
            file_name = file.get('file_name')
            file_path = file.get('file_path')
            created_at = file.get('created_at')

            #시간 포멧 설정 
            # created_at이 datetime 객체로 주어졌다고 가정함
            if isinstance(created_at, str):
                created_at = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S")
            formatted_created_at = created_at.strftime("%Y-%m-%d      %H:%M:%S").replace(" ", "&nbsp;")  # "YYYY-MM-DD HH:MM:SS" 형식

            # URL 경로 생성
            file_url = f"http://localhost:9501/download{file_path}"
            preview_url =f"http://localhost:9501/preview_file/?file_path={file_path}"

            data.append({
                FILE_NAME_COLUMN: file_name,
                CREATED_AT_COLUMN: formatted_created_at,
                FILE_PATH_COLUMN: f'<a href="{file_url}" target="_blank">{file_url}</a>',
                PREVIEW_COLUMN: f'<a href="{preview_url}" target="_blank"><img src="{preview_button_image_url}" alt="미리보기" style="width:50px;height:50px;"></a>',
            })
        
        # DataFrame 생성
        data_df = pd.DataFrame(data)

        # 인덱스를 1부터 시작하게 설정
        data_df.index = range(1, len(data_df) + 1)

        # HTML로 데이터프레임 표시
        st.markdown(data_df.to_html(escape=False), unsafe_allow_html=True)
        logger.info("display_mainboard 데이터프레임 표시")
    else:
        st.write("해당 날짜에 파일이 없습니다.")
        data_df = pd.DataFrame(columns=[FILE_NAME_COLUMN, CREATED_AT_COLUMN, FILE_PATH_COLUMN, PREVIEW_COLUMN, DOWNLOAD_CHECK_COLUMN])
        st.markdown(data_df.to_html(escape=False), unsafe_allow_html=True)

    # 사용자 세션 저장
    st.session_state.selected_user = selected_user
    st.session_state.selected_date = selected_date
    st.session_state.selected_user_id = selected_user_id