
from learner import RewardManager
from Object.Event import *
from simlator.dispatcher import *
from collections import defaultdict
from Object.Resource import *
from Object.Job import *

from learner.StateManager import *
from learner.RewardManager import *
from simlator.GanttChart import *

from Parameters import *
from DB_query import *

from model.Job_db import *
from model.Oper_db import *
from model.ProcessingTime_db import *
from model.Setup_db import *
from model.Demand_db import *
from model.machine_db import *

class Simulator:
    machine_list = {} #id로 객체 보관
    job_list = {} #lot id로 객체 보관
    number_of_machine = 0
    number_of_job = 0

    #todo 기본 값 세팅 해주어야함
    Q_time_table = {} # {"j0101" : 5 , "j0203" : 5}
    Processing_time_table = {} # {"j0101" : {"M1" : 5, "M2" : 10}, ...}
    Setup_table = {}  # {"M1" :{"J0":{"J1" : 5, "J2" :10},...}, "M2" :{"M1":5 , "M2":10}} #3중 딕셔너리..
    job_info = {} #max oper, job type, operation list

    dispatcher = Dispatcher()
    rewardManager = RewardManager()
    done = False #종료조건 판단
    runtime = 0 #시간
    plotlydf = pd.DataFrame([],columns=['Type','JOB_ID','Task','Start','Finish','Resource','Rule','Step','Q_diff','Q_check'])
    plotlydf_arrival_and_due = pd.DataFrame([],columns=['Type','JOB_ID','Task','Start','Finish','Resource','Rule','Step','Q_diff','Q_check'])
    step_number = 0
    event_list = []
    j = 0
    j2 = 0

    dataSetId = ''
    @classmethod
    def _init(cls, dataSetId):
        """
        machine에 먼저 접근 -> machine 객체 생성
        job에 접근 -> 비어있는 job dict만들기 , max_oper_of_job , opers_of_job
        setup에 접근 -> setup table만듬
        processing에 접근 -> processing table만듬
        oper에 접근 oper_of_job만듬
        demand에 접근 -> job 객체 생성
        """

        cls.dataSetId = dataSetId

        cls.get_job_info(cls.dataSetId)
        cls.get_machine(cls.dataSetId)


        cls.get_oper_info(cls.dataSetId)
        cls.get_lot(cls.dataSetId)
    @classmethod
    def reset(cls):
        # 리셋 부분
        cls.done = False #종료조건 판단
        cls.machine_list = defaultdict(Resource)
        cls.job_list = defaultdict(Job)
        cls.runtime = 0  # 시간
        cls.plotlydf = pd.DataFrame([], columns=['Type', 'JOB_ID', 'Task', 'Start', 'Finish', 'Resource', 'Rule', 'Step',
                                             'Q_diff', 'Q_check'])
        cls.plotlydf_arrival_and_due = pd.DataFrame([], columns=['Type', 'JOB_ID', 'Task', 'Start', 'Finish', 'Resource',
                                                             'Rule', 'Step', 'Q_diff', 'Q_check'])
        cls.step_number = 0
        cls.event_list = []
        cls.j = 0
        cls.j2 = 0

        cls.get_job_info(cls.dataSetId)
        cls.get_machine(cls.dataSetId)

        cls.get_oper_info(cls.dataSetId)
        cls.get_lot(cls.dataSetId)

        s = [0] * 24
        df = pd.Series(s)
        s = df.to_numpy()
        
        return s
    @classmethod
    def step(cls, action):
        done = False
        while True:
            machineId = cls.select_machine()
            if machineId == "NONE":
                cls.process_event()
                #이벤트도 비워져 있고, #job들도 다 done이면 종료
                if len(cls.event_list) == 0 and all(cls.job_list[job].status == "DONE" for job in cls.job_list):
                    done = True
                    s_prime = StateManager.set_state_36(cls.job_list, cls.machine_list, cls.runtime, cls.number_of_job)
                    df = pd.Series(s_prime)
                    s_prime = df.to_numpy()
                    r = 0
                    break
            else:
                candidate_list = cls.get_candidate(machineId)
                candidate_list, rule_name = cls.dispatcher.dispatching_rule_decision(candidate_list ,action, cls.runtime)
                cls.get_event(candidate_list[0], machineId, rule_name)

                s_prime = StateManager.set_state_36(cls.job_list, cls.machine_list, cls.runtime, cls.number_of_job)
                r , cls.machine_list = cls.rewardManager.get_reward(Parameters.reward_type, machineId , cls.job_list, cls.machine_list, cls.runtime)
                break
        return s_prime, r , done
    @classmethod
    def run(cls, rule):
        while True:
            machineId = cls.select_machine()
            if machineId != "NONE":
                candidate_list = cls.get_candidate(machineId)
                rule_number = Parameters.select_DSP_rule[rule]
                candidate_list, rule_name = cls.dispatcher.dispatching_rule_decision(candidate_list, rule_number, cls.runtime)
                cls.get_event(candidate_list[0], machineId, rule_name)
            else:
                if len(cls.event_list) == 0:
                    break
                cls.process_event()
                
        
        Flow_time, machine_util, util, makespan, tardiness, lateness, t_max,q_time_true,q_time_false,q_job_t, q_job_f, q_time = cls.performance_measure()
        gantt = GanttChart(cls.plotlydf, cls.plotlydf_arrival_and_due)
        if Parameters.gantt_on:
            gantt.play_gantt()


        print("FlowTime:" , Flow_time)
        print("machine_util:" , machine_util)
        print("util:" , util)
        print("makespan:" , makespan)
        print("Tardiness:" , tardiness)
        print("Lateness:" , lateness)
        print("T_max:" , t_max)
        print("Q time True", q_time_true)
        print("Q time False", q_time_false)
        print("Q job True", q_job_t)
        print("Q job False", q_job_f)
        print("Q total over time", q_time)
        return Flow_time, util, makespan
    #event = (job_type, operation, machine_type, start_time, end_time, event_type)

    @classmethod
    def gantt_chart(cls):
        if Parameters.gantt_on:
            gantt = GanttChart(cls.plotlydf, cls.plotlydf_arrival_and_due)
            gantt.play_gantt()
    @classmethod
    def process_event(cls):
        cls.event_list.sort(key = lambda x:x.end_time, reverse = False)
        event = cls.event_list.pop(0)
        cls.runtime = event.end_time
        if event.event_type == "job_arrival":
            event.job.arrival()
        else:
            if event.event_type != "track_in_finish":
                if event.event_type == "setup_change":
                    event_type = "setup"
                elif event.event_type == "NOTHING":
                    event_type = "NOTHING"
            else:
                #print(event.job)
                event_type = "j"+str(event.job.job_type)
                last = event.job.complete_setting(event.start_time, event.end_time ,event.event_type) # 작업이 대기로 변함, 시작시간, 종료시간, event_type
                event.machine.complete_setting(event.start_time, event.end_time ,event.event_type) # 기계도 사용가능하도록 변함
            rule = event.rule_name
            step = event.step_num
            start = datetime.fromtimestamp(event.start_time*3600)
            end = datetime.fromtimestamp(event.end_time*3600)
            q_time_diff = event.q_time_diff
            q_time_check = event.q_time_check
            #print(self.step_number) Q_Check , Q_time_over
            cls.plotlydf.loc[cls.j] = dict(Type = event_type, JOB_ID = event.job.id  ,Task=event.jop, Start=start, Finish=end, Resource=event.machine.id, Rule = rule,
                                             Step = step, Q_diff = q_time_diff, Q_check = q_time_check) #간트차트를 위한 딕셔너리 생성, 데이터프레임에 집어넣음
            cls.j+=1
    
    @classmethod
    def assign_setting(cls, job, machine,reservation_time): #job = 1 machine = 1
        q_time_diff = job.assign_setting(machine, cls.runtime)
        machine.assign_setting(job, reservation_time)
        return q_time_diff
    @classmethod
    def select_machine(cls):
        selected_machine = "NONE"
        for machineId in cls.machine_list:
            if cls.machine_list[machineId].status == "WAIT":
                #todo job_list를 분류 시켜놓을 필요가 있을듯
                # 예를 들어 현재 stocker에 있을 때 마다 이동? 번거롭더라도 스토커만 확인하는게 맞으니..
                # 종료된 작업이 있는 공간, stocker, 그리고 도착 예정 공간 세개로 나눠서 job을 배치
                for job in cls.job_list: #job 이름과 operation이름 찾기
                    if cls.job_list[job].status != "WAIT": #해당 jop가 작업중일 경우
                        pass
                    #TODO 해당 작업이 해당 기계에서 처리 가능한지 확인해야함
                    elif cls.can_process_oper_in_machine(cls.job_list[job] ,machineId) == False:
                        pass
                    else:
                        selected_machine = machineId
                        continue
                if selected_machine != "NONE":
                    continue
        return selected_machine

    @classmethod
    def get_candidate(cls, machineId):
        #todo machine_id와 machine 객체에 대한 구분이 명확해야 할듯
        candidate_list = []
        for job in cls.job_list:
            if cls.job_list[job].status == "WAIT":
                jobOperId = cls.job_list[job].current_operation_id
                setup_time = cls.machine_list[machineId].get_setup_time(cls.job_list[job].job_type)
                if cls.can_process_oper_in_machine(cls.job_list[job], machineId):
                    candidate_list.append([cls.job_list[job],cls.Processing_time_table[jobOperId][machineId], setup_time,jobOperId])

        return candidate_list

    @classmethod
    def get_event(cls, candidate, machineId, rule_name):
        step_num = cls.step_number
        job, process_time, setup_time, jop = candidate
        if setup_time != 0: #setup event 발생
            e = Event(job, "setup", cls.machine_list[machineId], cls.runtime, cls.runtime + setup_time,
                      "setup_change",
                      "NONE", step_num, setup_time, 0)
            cls.event_list.append(e)
        q_time_diff = cls.assign_setting(job, cls.machine_list[machineId],
                                          cls.runtime + setup_time + process_time)
        e = Event(job, jop, cls.machine_list[machineId], cls.runtime, cls.runtime + setup_time + process_time,
                  "track_in_finish", rule_name, step_num, setup_time, q_time_diff)
        cls.event_list.append(e)
        cls.step_number +=1

    @classmethod
    def get_machine(cls, dataSetId):
        #todo 해당 데이터 셋에 해당하는 기계정보를 전부 가져옴 -> 기계 id를
        #todo 기계 정보를 이용해 machine 객체들을 생성함
        # 생성한 객체들을 machine_list에 딕셔너리 형태로 저장함
        machines = DB_query.get_all_by_table(dataSetId, Machine_db)
        cls.number_of_machine = len(machines)
        for machine in machines:
            setup_time_table = cls.get_setup_time_table(dataSetId, machine)
            r = Resource(machine.machineId, machine.machineType, setup_time_table)
            cls.machine_list[machine.machineId] = r
    @classmethod
    def get_lot(cls, dataSetId):
        jobs = DB_query.get_all_by_table(dataSetId, Demand_db)
        for job in jobs:
            lot_id = job.demandId + "-" + job.jobId
            status = ("NOTYET" if job.arrivalData != 0 else "WAIT")
            oper_list = cls.job_info[job.jobId]["oper_list"]
            q_time_table = cls.get_q_time_table_of_opers(oper_list)

            j = Job(lot_id, job.jobId, cls.job_info[job.jobId]["job_type"] , cls.job_info[job.jobId]["max_oper"]
                    , job.duedate, job.arrivalData, status, oper_list, q_time_table)
            cls.job_list[lot_id] = j

    @classmethod
    def get_job_info(cls, dataSetId):
        jobs = DB_query.get_all_by_table(dataSetId, Job_db)
        cls.number_of_job = len(jobs)
        for job in jobs:
            job_info = {}
            job_info["max_oper"] = job.maxOper
            job_info["job_type"] = job.jobType
            oper_list = DB_query.get_all_operation_of_job(dataSetId,Oper_db,job.jobId)
            job_info["oper_list"] = oper_list
            cls.job_info[job.jobId] = job_info

    @classmethod
    def get_oper_info(cls, dataSetId):
        opers = DB_query.get_all_by_table(dataSetId, Oper_db)
        for oper in opers:
            cls.Q_time_table[oper.operId] = oper.operQtime
            for machineId in cls.machine_list:
                processing_time = DB_query.get_processing_time(dataSetId, ProcessingTime_db,oper.operId,
                                                               cls.machine_list[machineId].machine_type)
                if oper.operId not in cls.Processing_time_table:
                    cls.Processing_time_table[oper.operId] = {}
                cls.Processing_time_table[oper.operId][machineId] = processing_time

    @classmethod
    def get_setup_time_table(cls, dataSetId, machine):
        machine_setup_time_dict = {}
        for from_job_id in cls.job_info:
            from_to_setup_time_dict = DB_query.get_from_to_setup_time_dict(dataSetId,Setup_db,machine, from_job_id)
            machine_setup_time_dict[from_job_id] = from_to_setup_time_dict
        return machine_setup_time_dict

    @classmethod
    def get_q_time_table_of_opers(cls, oper_list): # 해당 job의
        q_time_table = {}
        for oper in oper_list:
            q_time_table[oper] = cls.Q_time_table[oper]
        return q_time_table

    @classmethod
    def can_process_oper_in_machine(cls, job, machineId):
        if cls.Processing_time_table[job.current_operation_id][machineId] == 0:
            return False
        else:
            return True
    @classmethod
    def performance_measure(cls):
        q_time_true = 0
        q_time_false = 0
        makespan = cls.runtime
        Flow_time = 0
        Tardiness_time = 0  # new
        Lateness_time = 0  # new
        T_max = 0  # new
        L_max = 0  # new
        value_time_table = []
        full_time_table = []
        machine_util = 0
        util = 0
        q_job_f = 0
        q_job_t = 0
        z = []
        total_q_time_over = 0
        for machineId in cls.machine_list:
            value_added_time, full_time = cls.machine_list[machineId].cal_util()
            value_time_table.append(value_added_time)
            full_time_table.append(full_time)
        util = sum(value_time_table) / sum(full_time_table)
        for jobId in cls.job_list:
            #todo jobFlow time 네이밍
            Flow_time += cls.job_list[jobId].job_flowtime
            if cls.job_list[jobId].tardiness_time > T_max:
                T_max = cls.job_list[jobId].tardiness_time
            Tardiness_time += cls.job_list[jobId].tardiness_time
            Lateness_time += cls.job_list[jobId].lateness_time
            k = []
            for q in cls.job_list[jobId].q_time_check_list.values():
                k.append(q)
                if q > 0:
                    q_time_false += 1
                else:
                    q_time_true += 1
            z.append(k)
            if cls.job_list[jobId].condition == True:
                q_job_t += 1
            else:
                q_job_f += 1
            total_q_time_over += cls.job_list[jobId].cal_q_time_total()
        # fig = px.timeline(self.plotlydf, x_start="Start", x_end="Finish", y="Resource", color="Task", width=1000, height=400)
        # fig.show()
        return Flow_time, machine_util, util, makespan, Tardiness_time, Lateness_time, T_max, q_time_true, q_time_false, q_job_t, q_job_f, total_q_time_over
