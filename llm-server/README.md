# LLM Server

## 명령어
```bash
# 개발서버: 
docker compose --env-file ./fastapi/app/.env.dev up --build -d 

#운영서버
docker compose --env-file ./fastapi/app/.env.prod up -d

```

## FastAPI
- 사용자가 FastAPI 서버로 HTTP 요청을 보냄
- FastAPI는 요청을 라우팅하고 관련된 엔드포인트 핸들러를 호출
- 비동기로 처리해야하는 작업이 있는 경우 Celery 작업을 호출

## Redis
- Celery의 작업은 Redis에 의해 관리되는 큐에 추가
- Redis는 메시지 브로커로서 큐에 들어온 작업을 보관하고, Celery 워커가 이 큐로부터 작업을 가져가도록 함
- Celery의 작업이 완료 되면 결과를 Redis에 저장

## Celery
- Celery 워커는 큐에 있는 작업을 Redis로부터 가져와서 처리