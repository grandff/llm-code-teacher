from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# 데이터베이스 모델 기본 클래스
Base = declarative_base()

class File(Base):
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False)
    gitlab_id = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
