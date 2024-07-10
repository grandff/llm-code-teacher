#!/bin/bash

# GitLab 서비스 초기화
gitlab-ctl reconfigure

# GitLab 서비스 시작
gitlab-ctl start

# 관리자 비밀번호 설정
echo "Setting GitLab root password..."
gitlab-rails runner "user = User.where(id: 1).first; user.password = 'ComplexPassword123!'; user.password_confirmation = 'ComplexPassword123!'; user.save!"


# 관리자 이메일 설정
echo "Setting GitLab root email..."
gitlab-rails runner <<'EOF'
user = User.where(id: 1).first

# 모든 이메일을 비활성화
user.emails.update_all(confirmed_at: nil)

new_email = 'root@example.com'  # 여기에 원하는 새로운 이메일을 설정하세요

# 새로운 이메일이 이미 있는지 확인하고 없다면 추가
unless Email.exists?(user: user, email: new_email)
  verified_email = Email.create!(user: user, email: new_email, confirmed_at: Time.now)
else
  verified_email = Email.find_by(user: user, email: new_email)
end

# 사용자 객체의 이메일과 커밋 이메일 업데이트
user.update!(email: new_email, commit_email: new_email)
EOF

# 사용자 객체의 이메일과 커밋 이메일 업데이트
user.update!(email: new_email, commit_email: new_email)

# GitLab 서비스 재시작
gitlab-ctl restart

# 컨테이너를 포그라운드에서 유지
tail -f /dev/null