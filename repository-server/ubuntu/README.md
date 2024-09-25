# ubuntu

## ssh 등록
```bash
//ssh 발급 위치 이동
cd ~/.ssh/

//터미널에서 ssh key 발급 
ssh-keygen -t rsa -b 4096 -C "root@example.com"

//개인 키를 에이전트 추가 
ssh-add ~/.ssh/id_rsa 

//공개 키 내용을 확인하고 복사
cat ~/.ssh/id_rsa.pub

//gitlab에 자신의 ssh 등록 

```

## ubuntu 컨테이너 접속
```bash
VScode에서 Dev Containers에 ubuntu 접속
```
![스크린샷 2024-09-23 오후 3 34 32](https://github.com/user-attachments/assets/423fa480-eaf4-4445-a3e9-4c76d0f42a3f)


## git 사용자 등록
```bash
//설정
git config --global user.name "Administrator"
git config --global user.email "root@example.com"

//확인
git config --global user.name
git config --global user.email
```
## git admin 설정
<img width="936" alt="스크린샷 2024-09-24 오전 8 31 41" src="https://github.com/user-attachments/assets/21296b5e-c566-4693-9fa8-79f3da41a783">

```bash
//프로젝트 등록
git remote add origin <Clone with SSH - gitlab url>

git add <파일명>
git commit -m <message>

//브런치 확인
git branch

//강제적으로 가져오기 
git pull origin main --allow-unrelated-histories


service ssh status
```


## gitlab과 ssh 통신 확인
```bash
service ssh start
service ssh status
```