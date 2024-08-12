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

# Streamlit 애플리케이션
def main():
    st.title("Hello, Streamlit!")

    conn = create_connection()

    # 사이드바에 날짜 선택 상자 생성
    st.sidebar.header("날짜 선택")
    available_dates = get_available_dates(conn)
    selected_date = st.sidebar.radio("날짜를 선택하세요", available_dates)

    # 선택된 날짜에 따라 사용자 리스트를 사이드바에 표시
    if selected_date:
        users_list = get_users_for_date(conn, selected_date)
        
        # 사이드바에 선택된 날짜의 사용자들 리스트 표시
        st.sidebar.header(f"{selected_date}의 사용자들")
        if users_list:
            for user in users_list:
                st.sidebar.write(f"- {user}")
        else:
            st.sidebar.write("선택된 날짜에 관련된 사용자가 없습니다.")

    conn.close()


if __name__ == "__main__":
    main()