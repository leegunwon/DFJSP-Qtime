import pymysql
import pandas as pd
db = pymysql.connect(
    host='localhost',
    port=3306, user='root',
    passwd='1234',
    db='fjsp_simulator_db',
    charset='utf8')

cursor = db.cursor()


insert_query = '''
INSERT INTO DataSet (dataSetId, dataDesc, createUser)
VALUES ('MK01', 'brandimate MK01 문제', 'hyungchan.shin');
'''

sql = '''
        CREATE TABLE DataSet (
    dataSetId VARCHAR(50) PRIMARY KEY,
    dataDesc VARCHAR(255),
    createUser VARCHAR(50),
    isUpdated TIMESTAMP,
    isCreated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''
sql2 = '''
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
'''
sql3 = '''
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
'''

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

"""
ALTER TABLE Job
ADD INDEX (jobId),
ADD INDEX (jobType);

기본키가 아닌 값을 다른 테이블에서 참조하려면 Index 만들어줘야함 
"""

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

insert_machine ='''
INSERT INTO Machines (MachineId, DataSetId, MachineType, MachineDesc)
SELECT 'M6', DataSetId, 'M6', 'MK01_M6'
FROM DataSet
WHERE DataSetId = 'MK01';

'''
# 6 5 5 5 6 6 5 5 6 6

insert_job ='''
INSERT INTO Job (jobId, DataSetId, jobType, jobDesc, maxOper)
SELECT 'j10', DataSetId, 'j10', 'MK01_J10', 6
FROM DataSet
WHERE DataSetId = 'MK01';

'''

import pandas as pd
import csv

"""process_time_table = pd.read_csv("MK01.csv",index_col=(0))
l = [6, 5, 5 ,5 ,6 ,6 ,5 ,5 ,6 ,6]
for i in range(1,11):
    for k in range(1, l[i-1] + 1):
        job_id = f'j{i:02}'
        oper_id = f'{job_id}{k:02}'
        for j in range(1,7):
            machineId = f'M{j:01}'
            processing_time = process_time_table[machineId].loc[oper_id]
            # jobId를 동적으로 생성
            insert_oper =f'''
        INSERT INTO ProcessingTime (dataSetId ,machineType, jobType, processingTime,operId)
        SELECT Oper.dataSetId, Machines.machineType, Oper.jobType,{processing_time}, Oper.operId
        FROM Oper
        JOIN Machines ON Machines.machineId = '{machineId}'
        WHERE Oper.operId = '{oper_id}' AND Oper.dataSetId = 'MK01';
        '''"""


            #cursor.execute(insert_oper)

#for i in range(10,11):
"""    # jobId를 동적으로 생성
    job_id = f'j{i:02}'
    demand_id = f'MK01_D_{i:03}'
    if k == l[i - 3]:
        check = True
    else:
        check = False
    insert_oper = f'''
    INSERT INTO Demand (jobId, DataSetId, demandId, arrivalData, dueDate)
    SELECT Job.jobId, DataSet.DataSetId, "{demand_id}", 0, 0
    FROM Job
    JOIN DataSet ON Job.dataSetId = DataSet.DataSetId
    WHERE DataSet.DataSetId = 'MK01' AND Job.jobId = '{job_id}';"""



for i in range(1, 7):
    for j in range(1,11):
        for k in range(1,11):
            machineId = f'M{i:01}'
            from_job_id = f'j{j:02}'
            to_job_id = f'j{k:02}'
            setup_time = 0
            insert_setup = f'''
                INSERT INTO Setup (dataSetId, machineId, machineType, fromJobType, toJobType, setupTime)
                SELECT JobTo.dataSetId, Machines.machineId, Machines.machineType, 
                       JobFrom.jobType as fromJobType, JobTo.jobType as toJobType, {setup_time}
                FROM Job as JobFrom, Job as JobTo
                JOIN Machines ON Machines.machineId = '{machineId}'
                WHERE JobTo.dataSetId = 'MK01'
                AND JobFrom.jobId = '{from_job_id}' AND JobTo.jobId = '{to_job_id}';
            '''

            cursor.execute(insert_setup)

db.commit()
db.close()
