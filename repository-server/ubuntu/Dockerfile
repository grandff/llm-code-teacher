# Ubuntu 20.04 기반 이미지 사용
FROM ubuntu:20.04

# 비대화형 모드로 설정
ENV DEBIAN_FRONTEND=noninteractive

# 타임존 설정을 위한 환경 변수 추가
ENV TZ=Asia/Seoul

# 기본 패키지 및 JDK 17 설치
RUN apt-get update && apt-get install -y \
    git \
    wget \
    openjdk-17-jdk \
    tzdata \
    && apt-get clean

# 타임존 설정을 비대화형으로 처리 (서울로 설정)
RUN ln -fs /usr/share/zoneinfo/Asia/Seoul /etc/localtime && \
    dpkg-reconfigure --frontend noninteractive tzdata

# 환경 변수 설정 (JDK 17을 기본 자바로 설정)
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

# Java 버전 확인 명령어 실행
RUN java -version