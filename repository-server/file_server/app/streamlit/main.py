import streamlit as st
import mysql.connector

def create_connection():
    connection = mysql.connector.connect(
        host="file_db",           # Docker Container name 
        port=3306,                # Docker Container name 내부 포트
        user="username",
        password="password",
        database="file_db"
    )
    return connection

# 사용 가능한 날짜 목록을 반환
def get_available_dates(conn):
    cursor = conn.cursor()
    query = "SELECT DISTINCT DATE_FORMAT(created_at, '%Y%m%d') AS date FROM files ORDER BY date DESC"
    cursor.execute(query)
    dates = cursor.fetchall()
    cursor.close()
    return [date[0] for date in dates]

# 선택된 날짜에 대한 사용자들의 리스트를 반환
def get_users_for_date(conn, selected_date):
    cursor = conn.cursor()
    query = """
    SELECT DISTINCT u.username
    FROM files f
    JOIN users u ON f.user_id = u.id
    WHERE DATE_FORMAT(f.created_at, '%Y%m%d') = %s
    """
    cursor.execute(query, (selected_date,))
    users = cursor.fetchall()
    cursor.close()
    return [user[0] for user in users]

def format_date(date_str):
    """날짜 문자열을 'YYYY-MM-DD' 형식으로 변환"""
    return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"


# 사용자 ID를 username으로 조회하는 함수
def get_user_id_by_username(conn, username):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id 
        FROM users 
        WHERE username = %s
    """, (username,))
    user_id = cursor.fetchone()
    cursor.close()
    return user_id[0] if user_id else None

# 선택된 날짜에 대한 파일 목록을 조회하는 함수
def get_files_for_date(conn, selected_date, username):
    user_id = get_user_id_by_username(conn, username)
    if not user_id:
        return []  # 사용자가 존재하지 않으면 빈 리스트 반환

    cursor = conn.cursor()
    cursor.execute("""
        SELECT file_name, file_path 
        FROM files 
        WHERE DATE(created_at) = %s AND user_id = %s
    """, (selected_date, user_id))
    files = cursor.fetchall()
    cursor.close()
    return files


def main():
    #st.title("Hello, Streamlit!")

    conn = create_connection()
    
    # 그룹 1
    st.sidebar.header("메뉴")
    
    # 사용 가능한 날짜 목록 가져오기
    available_dates = get_available_dates(conn)

    selected_user = None  # 선택된 사용자 저장
    selected_date = None  # 선택된 날짜 저장

    # 날짜를 메뉴 항목으로 추가
    for i, date in enumerate(available_dates, start=1):
        formatted_date = format_date(date)  # 날짜 형식 변환
        with st.sidebar.expander(f"{formatted_date}", expanded=False):
            users = get_users_for_date(conn, date)
            if users:
                for user in users:
                   if st.button(user, key=f"user_button_{i}_{user}", use_container_width=True):
                        selected_user = user  # 선택된 사용자 저장
                        selected_date = formatted_date  # 선택된 날짜 저장
            else:
                st.write("사용자가 없습니다.")


    # 선택된 날짜와 사용자들을 메인 화면에 표시
    if selected_date and selected_user:
        st.write(f"선택된 날짜: {selected_date}")
        st.write(f"선택된 사용자: {selected_user}")

        # 선택한 날짜에 대한 파일 리스트 가져오기
        files = get_files_for_date(conn, selected_date, selected_user)
        if files:
            st.write("선택된 날짜의 파일 리스트:")
            for file_name, file_path in files:
                st.write(f"- {file_name} (경로: {file_path})")
        else:
            st.write("해당 날짜에 파일이 없습니다.")

    conn.close()
    

if __name__ == "__main__":
    main()