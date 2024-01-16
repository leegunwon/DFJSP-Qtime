from src.learner.Algorithm.DQN import *
from src.learner.Algorithm.DQN_action_masking import *
from src.learner.Algorithm.DQN_CNN import *
from src.learner.Algorithm.DDQN import *


class Run_Simulator:
    def __init__(self):
        print("simulator on")
        Parameters.set_dataSetId(["sks_train_11", 'sks_train_12','sks_train_13','sks_train_14','sks_train_15'
                                  ,'sks_train_16', 'sks_train_17', 'sks_train_18', 'sks_train_19', 'sks_train_20'])  # 사용할 데이터셋 설정
        #Parameters.set_dataSetId(['sks_train_11'])
        Parameters.set_time_to_string() # 현 시간 가져오는 코드 -> 로그 및 기록을 위함
        Parameters.set_check_log(True)  # common 남기기 여부
        Parameters.set_check_down_parameter(True)  # DQN 파라미터 다운 여부
        Parameters.set_check_history_db(False)
        Parameters.set_check_gantt_on(True)  # 간트차트 띄우기 여부
        Parameters.set_meta_ver(False)
        Parameters.set_plan_horizon(840)

        Parameters.set_log_path() # 저장 경로 설정하는 코드

        # reward 설정
        #Parameters.set_reward_type("makespan") # reward 설정여
        Parameters.set_reward_type("util")
        #Parameters.set_reward_type("rtf")

        # state 설정
        Parameters.set_state_type("default_state")
        #Parameters.set_state_type("state_12")
        #Parameters.set_state_type("state_36")
        #Parameters.set_state_type("cnn")
        #Parameters.set_state_type("cnn_state")

        Simulator._init(Parameters.db_data)  # 데이터셋 선택 후 데이터에 맞게 시뮬레이터 설정

        # action 설정
        action_list = ["SPTSSU","SSU","EDD","MST","FIFO","LIFO"]         # 어떤 dsp rule을 쓸 것인가
        #ActionManager.set_action_type("setup" , action_list=action_list)
        #ActionManager.set_action_type("action_masking" , action_list=action_list)
        ActionManager.set_action_type("dsp_rule", action_list=action_list)


        Parameters.set_state_dimension(Simulator)
        print("set complete")


    def main(self, mode, algorithm):
        logging.info(f"mode: {mode}")
        logging.info(f"dsp_rule: {algorithm}")
        if mode == "learning":
            if algorithm == 'dqn':
                if ActionManager.action_type == "action_masking":
                    DQN_Action_Masking.main()
                else:
                    DQN.main()
            elif algorithm == 'ddqn':
                DDQN.main()
            elif algorithm == 'dqn_cnn':
                DQN_CNN.main()
            elif algorithm == 'PPO':
                PPO.main()
        elif mode == 'evaluate':
            if algorithm == "dqn":
                DQN.get_evaluate("/params_data/240115_230108", 500,
                                 ["sks_train_11", 'sks_train_12', 'sks_train_13', 'sks_train_14', 'sks_train_15'
                                     , 'sks_train_16', 'sks_train_17', 'sks_train_18', 'sks_train_19', 'sks_train_20'])
        elif mode == "result":
            if algorithm == 'dqn':
                DQN.get_result("/Users/shin/DFJSP-Qtime/params_data/240115_230108/1552param.pt", ["sks_train_11", 'sks_train_12','sks_train_13','sks_train_14','sks_train_15'
                                      ,'sks_train_16', 'sks_train_17', 'sks_train_18', 'sks_train_19', 'sks_train_20'])

if True:
    simulator = Run_Simulator()
    simulator.main("learning","ddqn") # dsp_rule = 개별 확인할 때만 사용하면 됨

# gantt chart 쑬 것인지
# 학습 방법, kpi목표
# 모든 디스패칭 룰 돌리기
