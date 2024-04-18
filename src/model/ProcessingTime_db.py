from datetime import datetime  # datetime 모듈 임포트

from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.orm import declarative_base  # 모듈 변경

Base = declarative_base()


class ProcessingTime_db(Base):
    __tablename__ = 'ProcessingTime'

    dataSetId = Column(String(50), primary_key=True)
    operId = Column(String(50), primary_key=True)
    jobType = Column(String(50), primary_key=True)
    machineType = Column(String(50), primary_key=True)
    processingTime = Column(Integer)
    isUpdated = Column(DateTime, default=datetime.now)  # 기본값 설정
    isCreated = Column(DateTime, server_default='CURRENT_TIMESTAMP')
