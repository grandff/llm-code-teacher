from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# 데이터베이스 설정
DATABASE_URL = "mysql+pymysql://username:password@file_db:3306/file_db"

# SQLAlchemy 엔진 및 세션 설정
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 데이터베이스 세션을 생성하는 종속성 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 데이터베이스 초기화
Base.metadata.create_all(bind=engine)
