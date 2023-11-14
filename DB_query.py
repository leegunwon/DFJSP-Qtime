from sqlalchemy import create_engine, Column, String, DateTime, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base  # 모듈 변경
from datetime import datetime  # datetime 모듈 임포트


class DB_query:
    host = 'localhost'
    port = 3306
    user = 'root'
    passwd = '1234'
    db = 'fjsp_simulator_db'
    charset = 'utf8'

    # SQLAlchemy 연결 엔진 생성
    db_url = f"mysql+pymysql://{user}:{passwd}@{host}:{port}/{db}?charset={charset}"
    engine = create_engine(db_url)

    Session = sessionmaker(bind=engine)
    session = Session()
    Base = declarative_base()

    @classmethod
    def get_all_by_table(cls, dataSetId, table):
        alls = cls.session.query(table).filter_by(dataSetId=dataSetId).all()
        return alls
    @classmethod
    def get_processing_time(cls, dataSetId, table, operId, machineType):
        # operId, machineType, dataSetId가 모두 일치하는 데이터 가져오기
        row = cls.session.query(table).filter_by(dataSetId=dataSetId, operId=operId,
                                                              machineType=machineType).first()
        return row.processingTime

    @classmethod
    def get_job_type(cls, dataSetId, table ,jobId):
        row = cls.session.query(table).filter_by(dataSetId=dataSetId, jobId = jobId).first()
        return row.jobType

    @classmethod
    def get_all_operation_of_job(cls, dataSetId, table, jobId):
        rows = cls.session.query(table).filter_by(dataSetId=dataSetId, jobId=jobId).all()
        oper_list = []
        for row in rows:
            oper_list.append(row.operId)
        return oper_list

    @classmethod
    def get_from_to_setup_time_dict(cls, dataSetId, table, machine, from_job_id):
        #todo job id가 아니라 job type으로 변경 해야함
        rows = cls.session.query(table).filter_by(dataSetId=dataSetId, fromJobType = from_job_id, machineId = machine.machineId).all()
        from_to_setup_time_dict ={}
        for row in rows:
            from_to_setup_time_dict[row.toJobType] = row.setupTime
        return from_to_setup_time_dict