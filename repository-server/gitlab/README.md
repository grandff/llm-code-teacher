# gitLab

## 설치 및 ID/PW 설정
```bash
git script/init.sh에 설정 
id: root
pw: ComplexPassword123! 
```


## git admin 설정
```bash
//설정
git config --global user.name "Administrator"
git config --global user.email "root@example.com"

//확인
git config --global user.name
git config --global user.email
```

## webhook 환경구축
1. amdin Area 클릭
![스크린샷 2024-07-11 오전 8 45 48](https://github.com/grandff/llm-code-teacher/assets/29056140/243a5a64-be41-4566-ba7c-c1b2bff6354e)

2. Setting > Network > Outbound requests> 클릭
![스크린샷 2024-07-11 오후 1 31 20](https://github.com/grandff/llm-code-teacher/assets/29056140/99c757ff-2f38-4c2d-a9cf-689636bc94e1)

3. Access Token 발생 
![스크린샷 2024-07-12 오전 9 35 32](https://github.com/user-attachments/assets/9befb8ac-fb6f-4676-955b-aaf7faa66b3f)

4. webhook 추가하기
![스크린샷 2024-07-12 오전 9 39 38](https://github.com/user-attachments/assets/aef7ea8e-9e17-4bc9-949b-08187f4c727a)


## 라이센스
```bash
MIT License
해당 소프트웨어를 누구라도 무상으로 제한없이 취급해도 좋다.
단, 저작권 표시 및 이 허가 표시를 소프트웨어의 모든 복제물 또는 중요한 부분에 기재해야 한다.
저자 또는 저작권자는 소프트웨어에 관해 아무런 책임을 지지 않는다.
레퍼런스
https://velog.io/@ssulv3030/MIT-license%EB%9E%80
http://developer.gaeasoft.co.kr/development-guide/gitlab/gitlab-introduce/
```



## 에러 해결
GitLab 구동 시, logrotate 서비스에서 멈춰 있는 문제 bash에 들어가 아래 명령어 구동
```bash
opt/gitlab/embedded/bin/runsvdir-start & gitlab-ctl reconfigure
//출처: https://hbesthee.tistory.com/2480 [채윤이네집:티스토리]
```

## 레퍼런스
webhook 정보
```bash
https://docs.gitlab.com/ee/user/project/integrations/webhooks.html
```

## Docker 자주 사용하는 명령어 
```bash
docker ps -al
docker exec -it <container_id> /bin/bash

//연결정보 확인
curl http://gitlab/
```



## webhook 외부도메인(안봐도됨)
```bash
webhook은 외부 도메인만 접속이 가능하다록 함 -> 내부주소를 외부주소로 바꾸는 ngrok 사용
https://dashboard.ngrok.com/get-started/setup/macos
로그인후 토큰 발행후 등록
ngrok config add-authtoken 2ixVALCltvax8EZxh9ZbIBTgfHU_4dEg6Fe98wFjsEmbv2tPu
ngrok http http://127.0.0.1:5000 명령어 사용하여 5000을 외부로 포트로 변경 
외부 url을 webhook에 등록
```



