import logging

import Parameters
from learner.DQN import *
from simlator.Simulator import *
from Parameters import *
import datetime
class Run_Simulator:
    def __init__(self):
        print("simulator on")

        Parameters.set_time_to_string()
        Parameters.set_log_path()
        Parameters.set_reward_type("makespan")
        Parameters.set_dataSetId("MK01")
        Simulator._init(Parameters.db_data)

        Parameters.set_check_log(True) # log 남기기 여부
        Parameters.set_check_down_parameter(True) # DQN 파라미터 다운 여부

        Parameters.set_check_gantt_on(False) #간트차트 띄우기 여부

    def main(self, mode, dsp_rule):
        print(Parameters.simulation_time, "--- simulator on ---")
        print("mode: ", mode)
        print("dsp_rule: ", dsp_rule)
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
                    #self.simulator.reset()
                    #self.simulator.run(Parameters.select_DSP_rule[i])


if True:
    simulator = Run_Simulator()
    simulator.main("DQN","MOR") # dsp_rule = 개별 확인할 때만 사용하면 됨

# gantt chart 쑬 것인지
# 학습 방법, kpi목표
# 모든 디스패칭 룰 돌리기
