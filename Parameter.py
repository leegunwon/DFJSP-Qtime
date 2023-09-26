

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

    r_param = {
        # 강화학습 파라미터
        "gamma": 0.99,
        "learning_rate": 0.0004,
        "batch_size": 64,
        "buffer_limit": 100000,
        "input_layer" : 36,
        "output_layer" : 10,
        "episode" : 10000
    }

    select_DSP_rule ={
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

def set_parameters(self, learning_rate, batch_size, num_epochs, hidden_size):
    # 파라미터 값을 설정합니다.
    self.learning_rate = learning_rate
    self.batch_size = batch_size
    self.num_epochs = num_epochs
    self.hidden_size = hidden_size

def get_parameters(self):
    # 파라미터 값을 반환합니다.
    return {
        'learning_rate': self.learning_rate,
        'batch_size': self.batch_size,
        'num_epochs': self.num_epochs,
        'hidden_size': self.hidden_size
    }


