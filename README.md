# LLM 기반 Code 리뷰 시스템

## 사용 전 필수 설치
1. network 생성
```bash
docker network create shared_network
```

## ollama 사용방법
1. docker compose로 컨테이너 모두 실행 여부 확인
2. ollama container로 들어가서 아래 명령어 입력
```bash
ollama run llama3
```
3. 모델 다운로드가 끝나면 사용
4. 만약 ollama 이미지가 실행이 안된다면 도커 메모리를 늘려서 다시 확인