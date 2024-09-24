# ubuntu


## git admin 설정
```bash
//설정
git config --global user.name "Administrator"
git config --global user.email "root@example.com"

//확인
git config --global user.name
git config --global user.email


//프로젝트 등록
git remote add origin <Clone with SSH>

git add <파일명>
git commit -m <message>

//브런치 확인
git branch


//강제적으로 가져오기 
git pull origin main --allow-unrelated-histories
```