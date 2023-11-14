import pymysql
import pandas as pd
from collections import Counter
from Parameters import *

host = Parameters.db_setting["host"]
port = Parameters.db_setting["port"]
user = Parameters.db_setting["user"]
passwd = Parameters.db_setting["passwd"]
database = Parameters.db_setting["db"]
charset = Parameters.db_setting["charset"]

db = pymysql.connect(
    host= host ,
    port = port, user = user,
    passwd = passwd,
    db = database,
    charset = charset)

cursor = db.cursor()

#create table
create_dataSet = '''
        CREATE TABLE DataSet (
    dataSetId VARCHAR(50) PRIMARY KEY,
    dataDesc VARCHAR(255),
    createUser VARCHAR(50),
    isUpdated TIMESTAMP,
    isCreated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''
create_machine = """
CREATE TABLE Machines (
    machineId VARCHAR(50),
    dataSetId VARCHAR(50),
    machineType VARCHAR(255),
    machineDesc VARCHAR(255),
    isUpdated TIMESTAMP,
    isCreated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    PRIMARY KEY (machineId, DataSetId),
    FOREIGN KEY (dataSetId) REFERENCES DataSet(dataSetId)
);
"""
create_Job ="""
    CREATE TABLE Job (
    dataSetId VARCHAR(50),
    jobId VARCHAR(50),
    jobType VARCHAR(255),
    jobDesc VARCHAR(255),
    maxOper INT,
    isUpdated TIMESTAMP,
    isCreated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (jobId, dataSetId),
    FOREIGN KEY (dataSetId) REFERENCES DataSet(DataSetId)
);
"""
created_oper = '''
CREATE TABLE Oper (
    dataSetId VARCHAR(50),
    jobId VARCHAR(50),
    jobType VARCHAR(255),
    operId VARCHAR(50),
    lastOper BOOLEAN,  -- BOOLEAN 데이터 타입은 1 또는 0 값을 가집니다.
    operDesc VARCHAR(255),
    operQtime INT,
    isUpdated TIMESTAMP,
    isCreated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (jobId, dataSetId, operId),
    FOREIGN KEY (dataSetId) REFERENCES DataSet(DataSetId),
    FOREIGN KEY (jobId) REFERENCES Job(jobId),
    FOREIGN KEY (jobType) REFERENCES Job(jobType)
);
'''
created_index ='''
ALTER TABLE Job
ADD INDEX (jobId),
ADD INDEX (jobType);
'''
created_Setup = '''
CREATE TABLE Setup (
    dataSetId VARCHAR(50),
    machineId VARCHAR(50),
    machineType VARCHAR(255),
    fromJobType VARCHAR(50),
    toJobType VARCHAR(50),
    setupTime INT,
    isUpdated TIMESTAMP,
    isCreated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (machineId, dataSetId, machineType, fromJobType, toJobType),
    FOREIGN KEY (dataSetId) REFERENCES DataSet(DataSetId),
    FOREIGN KEY (machineId) REFERENCES Machines(machineId),
    FOREIGN KEY (machineType) REFERENCES Machines(machineType)
);
'''
created_ProcessingTime = '''
CREATE TABLE ProcessingTime (
    dataSetId VARCHAR(50),
    operId VARCHAR(50),
    jobType VARCHAR(50),
    machineType VARCHAR(50),
    processingTime INT,
    isUpdated TIMESTAMP,
    isCreated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (operId, dataSetId, machineType, jobType),
    FOREIGN KEY (dataSetId) REFERENCES DataSet(DataSetId),
    FOREIGN KEY (operId) REFERENCES Oper(operId),
    FOREIGN KEY (machineType) REFERENCES Machines(machineType),
    FOREIGN KEY (jobType) REFERENCES Job(jobType)
);
'''
created_Demand = '''
CREATE TABLE Demand (
    dataSetId VARCHAR(50),
    demandId VARCHAR(50),
    jobId VARCHAR(50),
    arrivalData INT,
    dueDate INT,
    isUpdated TIMESTAMP,
    isCreated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (dataSetId, demandId),
    FOREIGN KEY (dataSetId) REFERENCES DataSet(DataSetId)
);
'''

def insert_dataSetId(dataSetId, dataDesc, createUser):
    insert_query = f'''
    INSERT INTO DataSet (dataSetId, dataDesc, createUser)
    VALUES ('{dataSetId}', '{dataDesc}', '{createUser}');
    '''
    cursor.execute(insert_query)
def insert_machine(dataSetId, p_data):
    number_of_machine = 0
    for machineId in p_data.columns:
        number_of_machine += 1
        insert_machine = f'''
        INSERT INTO Machines (MachineId, DataSetId, MachineType, MachineDesc)
        SELECT '{machineId}', '{dataSetId}', '{machineId}', '{dataSetId}_{machineId}'
        FROM DataSet
        WHERE DataSetId = '{dataSetId}';
        '''
        cursor.execute(insert_machine)
    return number_of_machine
def insert_Job_oper(dataSetId, p_data, q_data = pd.DataFrame()):
    job_list = []
    oper_list = []
    for i in range(p_data.shape[0]):
        job_oper = p_data.iloc[i].name
        job_list.append(job_oper[:3])

    count_oper_dict = dict(Counter(job_list))
    for k, v in count_oper_dict.items():
        oper_list.append(v)
        insert_job = f'''
        INSERT INTO Job (jobId, DataSetId, jobType, jobDesc, maxOper)
        SELECT '{k}', DataSet.dataSetId, '{k}', '{dataSetId}_{k}', '{v}'
        FROM DataSet
        WHERE DataSetId = '{dataSetId}';
        '''
        cursor.execute(insert_job)
        for oper in range(1, v+1):
            oper_id = f'{k}{oper:02}'
            if q_data.empty:
                q_time = 0
            else:
                q_time = q_data.loc[k, str(oper)]
            insert_oper = f'''
            INSERT INTO Oper (jobId, DataSetId, jobType, operId, lastOper, operDesc, operQtime)
            SELECT Job.jobId, DataSet.dataSetId, Job.jobId, '{oper_id}', '{1 if oper == v else 0}', '{oper_id}', '{q_time}'
            FROM DataSet
            JOIN Job ON Job.dataSetId = DataSet.DataSetId
            WHERE DataSet.DataSetId = '{dataSetId}' AND Job.jobId = '{k}';
            

            '''
            cursor.execute(insert_oper)
    number_of_job = len(count_oper_dict)
    return number_of_job, oper_list
def insert_Setup(dataSetId, number_of_mahicne, number_of_job, s_data = pd.DataFrame()):
    for i in range(1, number_of_mahicne+1):
        for j in range(1, number_of_job + 1):
            for k in range(1, number_of_job+1):
                machineId = f'M{i:01}'
                from_job_id = f'j{j:02}'
                to_job_id = f'j{k:02}'
                if s_data.empty:
                    setup_time = 0
                else:
                    setup_time = s_data[to_job_id].loc[from_job_id]
                print(from_job_id, to_job_id)
                insert_setup = f'''
                    INSERT INTO Setup (dataSetId, machineId, machineType, fromJobType, toJobType, setupTime)
                    SELECT JobTo.dataSetId, Machines.machineId, Machines.machineType, 
                           JobFrom.jobType, JobTo.jobType, '{setup_time}'
                    FROM Job as JobFrom, Job as JobTo
                    JOIN Machines ON Machines.machineId = '{machineId}' AND Machines.dataSetId = '{dataSetId}'
                    WHERE JobTo.dataSetId = '{dataSetId}' and JobFrom.dataSetId = '{dataSetId}'
                    AND JobFrom.jobId = '{from_job_id}' AND JobTo.jobId = '{to_job_id}';
                '''
                print(insert_setup)
                cursor.execute(insert_setup)
def insert_ProcessingTime(dataSetId, p_data ,number_of_job , number_of_machine, oper_list):
    for i in range(1, number_of_job+1):
        for k in range(1, oper_list[i - 1] + 1):
            job_id = f'j{i:02}'
            oper_id = f'{job_id}{k:02}'
            for j in range(1, number_of_machine+1):
                machineId = f'M{j:01}'
                processing_time = p_data[machineId].loc[oper_id]
                # jobId를 동적으로 생성
                insert_oper = f'''
            INSERT INTO ProcessingTime (dataSetId ,machineType, jobType, processingTime,operId)
            SELECT Oper.dataSetId, Machines.machineType, Oper.jobType,'{processing_time}', Oper.operId
            FROM Oper
            JOIN Machines ON Machines.machineId = '{machineId}' AND Machines.dataSetId = '{dataSetId}'
            WHERE Oper.operId = '{oper_id}' AND Oper.dataSetId = '{dataSetId}';
            '''

                cursor.execute(insert_oper)
def insert_Demand(dataSetId, number_of_job ,rd_data=pd.DataFrame()):
    if rd_data.empty:
        for i in range(1, number_of_job+1):
            # jobId를 동적으로 생성
            job_id = f'j{i:02}'
            demand_id = f'{dataSetId}_D_{i:03}'
            insert_oper = f'''
            INSERT INTO Demand (jobId, DataSetId, demandId, arrivalData, dueDate)
            SELECT Job.jobId, DataSet.DataSetId, '{demand_id}', 0, 0
            FROM Job
            JOIN DataSet ON Job.dataSetId = DataSet.DataSetId 
            WHERE DataSet.DataSetId = '{dataSetId}' AND Job.jobId = '{job_id}';
            '''
            cursor.execute(insert_oper)
    else:
        for j in range(rd_data.shape[0]):
            job_id = rd_data.iloc[j].name
            demand_id = f'{dataSetId}_D_{job_id}_{j:03}'
            arrival_time = rd_data.iloc[j, 0]
            due_date = rd_data.iloc[j, 1]
            insert_oper = f'''
                        INSERT INTO Demand (jobId, DataSetId, demandId, arrivalData, dueDate)
                        SELECT Job.jobId, Job.dataSetId, '{demand_id}', '{arrival_time}', '{due_date}'
                        FROM Job
                        WHERE Job.DataSetId = '{dataSetId}' AND Job.jobId = '{job_id}';
                        '''
            cursor.execute(insert_oper)


def insert_db(dataSetId, dataDesc ,create_user ,p_data, s_data = None, rd_data = None, q_data =None):


    insert_dataSetId(dataSetId, dataDesc, create_user)
    print("clear_dataSetId")
    number_of_machine = insert_machine(dataSetId,p_data)
    print("clear_machine")
    number_of_job, oper_list = insert_Job_oper(dataSetId, p_data ,q_data)
    print("clear_job")
    insert_Setup(dataSetId, number_of_machine, number_of_job, s_data)
    print("clear_setup")
    insert_ProcessingTime(dataSetId, p_data, number_of_job, number_of_machine, oper_list)
    print("clear_ptime")
    insert_Demand(dataSetId, 5, rd_data)
    print("clear_demand")
    db.commit()
    db.close()


"""
    >>> 사용법
    >>> 저장하고 싶은 DataSetId, 설명, 생성유저 설정
    >>> 저장하고 싶은 데이터셋 csv파일 삽입
    >>> 만약 setup없는 문제인 경우 p_data만 아닌경우 모든 데이


"""

insert_db(
    dataSetId= "DFJSP_10_60_0.4",
    dataDesc = "DFJSP mac_10 arrive_60, q_0.4",
    create_user = "hyungchan_shin",
    p_data = pd.read_csv("/Users/shin/DFJSP-Qtime/test_data/FJSP_Sim_10_zero.csv", index_col=(0)),
    s_data = pd.read_csv("/Users/shin/DFJSP-Qtime/test_data/FJSP_Set_10.csv",index_col=(0)),
    rd_data = pd.read_csv("/Users/shin/DFJSP-Qtime/test_data/rd_time/10/FJSP_rd_time_10_10,60.csv",index_col=(0)),
    q_data = pd.read_csv("/Users/shin/DFJSP-Qtime/test_data/Q-time/FJSP_Q_time_10_0.4.csv",index_col=(0))

)



