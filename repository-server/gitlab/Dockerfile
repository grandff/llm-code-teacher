# 베이스 이미지를 gitlab/gitlab-ce로 설정
FROM gitlab/gitlab-ce:latest

# 환경 변수 설정: 비대화형 모드로 설정
ENV DEBIAN_FRONTEND=noninteractive

# 타임존 설정을 위한 환경 변수 추가
ENV TZ=Asia/Seoul

# OpenSSH 서버 및 기타 패키지 설치
RUN apt-get update && apt-get install -y \
    git \
    openssh-server \
    tzdata \
    && apt-get clean

# 타임존 설정을 비대화형으로 처리 (서울로 설정)
RUN ln -fs /usr/share/zoneinfo/Asia/Seoul /etc/localtime && \
    dpkg-reconfigure --frontend noninteractive tzdata

# SSH 서비스 디렉토리 생성
RUN mkdir /var/run/sshd

# 필요한 파일을 컨테이너에 복사
COPY scripts /scripts

# 스크립트에 실행 권한 부여
RUN chmod +x /scripts/*.sh

# 커스텀 entrypoint 설정
ENTRYPOINT ["/scripts/init.sh"]
