def format_date(date_str):
    """날짜 문자열을 'YYYY-MM-DD' 형식으로 변환"""
    return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
