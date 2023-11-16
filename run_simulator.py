import Parameters
from learner.DQN import *
from metaheuristic.FJSP_GA import *
from metaheuristic.FJSP_2SGA import *

class Run_Simulator:
    def __init__(self):
        print("simulator on")
        Parameters.set_dataSetId("DFJSP_10_60_0.4")  # 사용할 데이터셋 설정
        Parameters.set_time_to_string() # 현재 시간 가져오는 코드 -> 로그 및 기록을 위함
        Parameters.set_check_log(False)  # log 남기기 여부
        Parameters.set_check_down_parameter(False)  # DQN 파라미터 다운 여부
        Parameters.set_check_history_db(False)
        Parameters.set_check_gantt_on(True)  # 간트차트 띄우기 여부
        Parameters.set_meta_ver(False)
        DataInventory.set_db_data()

        Parameters.set_log_path() # 저장 경로 설정하는 코드
        Parameters.set_reward_type("makespan") # reward 설정
        Simulator._init(Parameters.db_data) # 데이터셋 선택 후 데이터에 맞게 시뮬레이터 설정

        Parameters.set_state_dimension(Simulator)
        print("set complete")
    def main(self, mode, dsp_rule):
        logging.info(f"mode: {mode}")
        logging.info(f"dsp_rule: {dsp_rule}")
        if mode == "DQN":
             Flow_time, machine_util, util, makespan, score, makespan_list, q_over_time_list, score_list = DQN.main()
             print(makespan_list, q_over_time_list )
             DQN.plot_pareto(makespan_list, q_over_time_list, score_list)
        elif mode == "DSP_run":
            Simulator.run(dsp_rule)
            #self.simulator.run(dsp_rule)
        elif mode == "DSP_check_run":
            for i in Parameters.DSP_rule_check:
                if Parameters.DSP_rule_check[i]:
                    print(i)
                    Simulator.run(i)
                    Simulator.reset()
        elif mode == "meta_heuristics":
            start_time = time.time()
            k = []
            #GA_FJSP.search()
            FJSP_2SGA.search()




if True:
    simulator = Run_Simulator()
    simulator.main("DSP_run","SPT") # dsp_rule = 개별 확인할 때만 사용하면 됨

# gantt chart 쑬 것인지
# 학습 방법, kpi목표
# 모든 디스패칭 룰 돌리기
