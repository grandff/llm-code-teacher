# Ubuntu 20.04 기반 이미지 사용
FROM ubuntu:20.04

# 환경 변수 설정
ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:1
# USER 환경 변수 설정
ENV USER=root  

# 기본 패키지 업데이트 및 설치
RUN apt-get update && apt-get install -y \
    xfce4 \
    xfce4-goodies \
    tightvncserver \
    dbus-x11 \
    x11-xserver-utils \
    novnc \
    websockify \
    git \ 
    python3 \
    python3-pip \
    && apt-get clean

# VNC 서버 초기 설정
RUN mkdir -p /root/.vnc \
    && echo "password" | vncpasswd -f > /root/.vnc/passwd \
    && chmod 600 /root/.vnc/passwd

# xstartup 파일 생성 및 실행 권한 부여
RUN echo '#!/bin/bash\nxrdb $HOME/.Xresources\nstartxfce4 &' > /root/.vnc/xstartup \
    && chmod +x /root/.vnc/xstartup

# 포트 5900 (VNC)과 80 (noVNC) 열기
EXPOSE 5900 80

# VNC 서버 실행 명령어 (noVNC 포함)
CMD /bin/bash -c "vncserver :1 && websockify --web=/usr/share/novnc/ 80 localhost:5900"
