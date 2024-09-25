#!/bin/bash

# 로그 파일 경로 설정
LOG_FILE="/var/log/gitlab_setup.log"

# 로그 파일에 출력 저장
exec > >(tee -a ${LOG_FILE} ) 2>&1

# SSH 서비스 시작
echo "Starting SSH service..."
service ssh start

# GitLab의 runit 서비스 디렉토리 시작 (백그라운드에서 실행)
echo "Starting runit service directory..."
/opt/gitlab/embedded/bin/runsvdir-start &

# runit 서비스가 안정적으로 시작될 시간을 확보하기 위해 잠시 대기
sleep 5

# GitLab 서비스 초기화
gitlab-ctl reconfigure

# 관리자 비밀번호 설정
echo "Setting GitLab root password..."
gitlab-rails runner "user = User.where(id: 1).first; user.password = 'ComplexPassword123!'; user.password_confirmation = 'ComplexPassword123!'; user.save!"

# 관리자 이메일 설정
echo "Setting GitLab root email..."
gitlab-rails runner "user = User.find(1); Email.create!(user: user, email: 'root@example.com', confirmed_at: Time.now) unless Email.exists?(user: user, email: 'root@example.com'); user.update!(email: 'root@example.com', commit_email: 'root@example.com')"

# GitLab 서비스 재시작
gitlab-ctl restart


# 컨테이너를 포그라운드에서 유지
tail -f /dev/null