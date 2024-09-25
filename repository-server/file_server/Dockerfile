# 베이스 이미지로 Python 3.12 버전 사용
FROM python:3.12

# 비대화형 모드로 설정
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_NO_INPUT=1

# 필요한 패키지 업데이트 및 curl, supervisor 설치
RUN apt-get update && apt-get install -y curl supervisor && apt-get clean

# 워킹 디렉터리 설정
WORKDIR /app

# requirements.txt를 컨테이너에 복사
COPY ./app/requirements.txt /app/

# requirements.txt에 명시된 패키지 설치
RUN pip install --no-cache-dir -r /app/requirements.txt

# 애플리케이션 파일을 컨테이너에 복사
COPY ./app /app

# supervisord.conf 파일을 컨테이너에 복사
COPY ./supervisord.conf /app/supervisord.conf

# 로그 디렉토리 생성
RUN mkdir -p /var/log/supervisor && \
    chown -R www-data:www-data /var/log/supervisor

# 포트 설정(FastAPI,Streamlit)
EXPOSE 8000  
EXPOSE 8501

# 엔트리포인트 설정
CMD ["supervisord", "-c", "/app/supervisord.conf"]