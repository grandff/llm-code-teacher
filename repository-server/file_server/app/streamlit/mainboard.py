import pandas as pd
import streamlit as st
from database import get_files_for_date
import requests
import httpx
import asyncio
import os
from fastapi.responses import FileResponse


# 상수 정의
DOWNLOAD_CHECK_COLUMN = "다운로드 체크"
FILE_NAME_COLUMN = "파일이름"
CREATED_AT_COLUMN = "생성시간"
FILE_PATH_COLUMN = "다운로드 링크"

# 페이지 설정
#st.set_page_config(layout="wide")  # 페이지 레이아웃을 넓게 설정
def display_mainboard(conn, selected_date, selected_user,selected_user_id):
    
    # 선택한 날짜에 대한 파일 리스트 가져오기
    files = get_files_for_date(conn, selected_date, selected_user_id)
    if files:
        data = []
        for id, user_id, file_name, file_path, created_at in files:
            data.append({
                FILE_NAME_COLUMN: file_name,
                CREATED_AT_COLUMN: created_at,
                FILE_PATH_COLUMN: "http://localhost:9501/download"+file_path,
                DOWNLOAD_CHECK_COLUMN: False
            })
        data_df = pd.DataFrame(data)
    else:
        st.write("해당 날짜에 파일이 없습니다.")
        data_df = pd.DataFrame(columns=[FILE_NAME_COLUMN, CREATED_AT_COLUMN, FILE_PATH_COLUMN, DOWNLOAD_CHECK_COLUMN])
    
    
    # 세션 상태에서 체크박스 상태 가져오기
    session_key = f"{DOWNLOAD_CHECK_COLUMN}_{selected_date}_{selected_user}"
    if session_key not in st.session_state:
        st.session_state[session_key] = [False] * len(data_df)  # 세션에 값이 없으면 초기 상태 설정
    
    # 데이터프레임에 체크박스 상태 반영
    for i in range(len(data_df)):
        if st.session_state[session_key]:  # 세션에 값이 있으면 가져옴
            data_df.at[i, DOWNLOAD_CHECK_COLUMN] = st.session_state[session_key][i]
        else:
            data_df.at[i, DOWNLOAD_CHECK_COLUMN] = False  # 기본값은 False

    # 데이터프레임 표시
    edited_df = st.dataframe(
        data_df,
        column_config={
            DOWNLOAD_CHECK_COLUMN: st.column_config.CheckboxColumn(help="want download check"),
            FILE_PATH_COLUMN : st.column_config.LinkColumn(FILE_PATH_COLUMN),
        },
        hide_index=False
    )

    # 사용자 세션 저장
    st.session_state.selected_user = selected_user
    st.session_state.selected_date = selected_date
    st.session_state.selected_user_id = selected_user_id