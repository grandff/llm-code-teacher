import streamlit as st
import requests
import logging


# 로그 설정
logger = logging.getLogger(__name__)

# 파일이 있는 날짜 반환
def get_available_dates():
    try:
        response = requests.get("http://file_server:8000/available_dates")
        response.raise_for_status() 
        data = response.json()  
        available_dates = data.get("dates", [])
        return available_dates
    except requests.RequestException as e:
        print(f"Error fetching available dates: {e}")
        return []
    

# 선택된 날짜에 대한 사용자들의 리스트를 반환
def get_users_for_date(selected_date):
    try:
        # FastAPI 엔드포인트 호출
        url = "http://file_server:8000/users_for_date"
        params = {"selected_date": selected_date}
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            users = data.get('userList', [])
            logger.error(f"users: {users}")
            return users
        else:
            print(f"Failed to retrieve users: {response.status_code}")
            return []
    
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []


def get_files_for_date(selected_date: str, user_id: int):
    try:
        # FastAPI 엔드포인트 호출
        url = "http://file_server:8000/files_for_date"
        params = {"selected_date": selected_date, "user_id": user_id}
        
        # 요청 보내기
        response = requests.get(url, params=params)
        
        # 응답 상태 확인
        if response.status_code == 200:
            data = response.json()
            # 'fileList' 키로 파일 목록을 추출
            file_list = data.get("fileList", [])
            logger.error(f"file_list : {file_list}")
            return file_list
        else:
            print(f"Failed to retrieve files: {response.status_code}")
            return []
    
    except Exception as e:
        print(f"Error fetching files: {e}")
        return []