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
    SELECT DISTINCT u.username, u.id
    FROM files f
    JOIN users u ON f.user_id = u.id
    WHERE DATE_FORMAT(f.created_at, '%Y%m%d') = %s
    """
    cursor.execute(query, (selected_date,))
    users = cursor.fetchall()
    cursor.close()
    return users


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
def get_files_for_date(conn, selected_date, user_id):

    cursor = conn.cursor()
    cursor.execute("""
        SELECT *
        FROM files 
        WHERE DATE(created_at) = %s AND user_id = %s
    """, (selected_date, user_id))
    files = cursor.fetchall()
    cursor.close()
    return files