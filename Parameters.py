
import datetime
import logging
#todo 파라미터 정리 필요, 강화학습 -> 하이퍼 파라미터
class Parameters:
    """
    "p_data" : "/Users/shin/DFJSP-Qtime/Data/DFJSP_test.csv",
    "s_data" : "/Users/shin/DFJSP-Qtime/Data/DFJSP_setup_test.csv",
    "q_data" : "/Users/shin/DFJSP-Qtime/Data/DFJSP_Qdata_test.csv",
    "rd_data" : "/Users/shin/DFJSP-Qtime/Data/DFJSP_rdData_test2.csv"
    """
    # 여기에 파라미터를 초기화합니다.'
    print("parameter load")
    data = {
        # 데이터 링크
        "p_data" : "/Users/shin/DFJSP-Qtime/test_data/FJSP_Sim_10_zero.csv",
        "s_data" : "/Users/shin/DFJSP-Qtime/test_data/FJSP_Set_10.csv",
        "q_data" : "/Users/shin/DFJSP-Qtime/test_data/Q-time/FJSP_Q_time_10_0.4.csv",
        "rd_data" : "/Users/shin/DFJSP-Qtime/test_data/rd_time/10/FJSP_rd_time_10_10,60.csv"
    }

    db_data = "MK01"

    r_param = {
        # 강화학습 파라미터
        "gamma": 0.99,
        "learning_rate": 0.0004,
        "batch_size": 64,
        "buffer_limit": 100000,
        "input_layer" : 24,
        "output_layer" : 10,
        "episode" : 10000
    }

    select_DSP_rule ={
        #DSP rule에 해당하는 번호
        "SPT" : 0,
        "SSU" : 1,
        "SPTSSU" : 2,
        "MOR" : 3,
        "LOR" : 4,
        "EDD" : 5,
        "MST" : 6,
        "FIFO" : 7,
        "LIFO" : 8,
        "CR" : 9,
        "SQT" : 11
    }

    DSP_rule_check ={
        #DSP_run에서 사용할 check
        "SPT": True,
        "SSU": True,
        "SPTSSU": True,
        "MOR": True,
        "LOR": True,
        "EDD": True,
        "MST": True,
        "FIFO": True,
        "LIFO": True,
        "CR": True,
        "SQT" : True

    }


    gantt_on ={
        "mahicne_on_job_number" : False,
        "machine_gantt" : False,
        "DSP_gantt" : True,
        "step_DSP_gantt" : False,
        "heatMap_gantt" : False,
        "main_gantt" : True,
        "job_gantt_for_Q_time" : True
    }

    gantt_on = True # 간트 껏다 키기
    log_on = True #log 껐다 키기
    param_down_on = True #파라미터 다운 끄기


    reward_type = "makespan"

    simulation_time = ""
    save_log_directory = "/Users/shin/DFJSP-Qtime/log_data/"
    save_parameter_directory = "/Users/shin/DFJSP-Qtime/params_data/"

    log_path = ""

    @classmethod
    def set_check_gantt_on(cls, check_gantt):
        cls.gantt_on = check_gantt

    @classmethod
    def set_check_log(cls, check_log):
        cls.log_on = check_log

    @classmethod
    def set_time_to_string(cls):
        current_time = datetime.datetime.now()
        # 원하는 문자열 형식으로 시간을 포맷팅
        time_format = "%y%m%d_%H%M%S"  # "년월일_시분" 형태의 포맷
        current_time_str = current_time.strftime(time_format)
        cls.simulation_time = current_time_str

    @classmethod
    def set_check_down_parameter(cls, check_param):
        cls.param_down_on = check_param

    @classmethod
    def set_reward_type(cls, reward_type):
        cls.reward_type = reward_type

    @classmethod
    def set_log_path(cls):
        log_path = cls.save_log_directory + cls.simulation_time + "performance.log"
        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,  # 로그 레벨을 INFO로 설정
            format='%(asctime)s [%(levelname)s]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    @classmethod
    def set_dataSetId(cls, dataSetId):
        cls.db_data = dataSetId


