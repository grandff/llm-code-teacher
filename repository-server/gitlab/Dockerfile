# 베이스 이미지를 gitlab/gitlab-ce로 설정
FROM gitlab/gitlab-ce:latest

# 필요한 파일을 컨테이너에 복사
COPY scripts /scripts

# 스크립트에 실행 권한 부여
RUN chmod +x /scripts/*.sh

# 커스텀 entrypoint 설정
ENTRYPOINT ["/scripts/init.sh"]
