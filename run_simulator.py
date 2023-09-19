from DQN import *
from simulator_DFJSP import *
from Parameter import *

class Run_Simulator:
    def __init__(self):
        print("simulator on")
        self.params = Parameters()
        self.DQN = DQN(self.params.data, self.params.r_param)
        self.simulator = FJSP_simulator(self.params.data["p_data"],self.params.data["s_data"],
                                        self.params.data["q_data"],self.params.data["rd_data"])

    def main(self, mode, dsp_rule):
        if mode == "DQN":
             self.DQN.main()
        elif mode == "DSP_run":
            self.simulator.run(dsp_rule)
        elif mode == "DSP_check_run":
            for i in self.params.DSP_rule_check:
                if self.params.DSP_rule_check[i]:
                    print(i)
                    self.simulator.reset()
                    self.simulator.run(self.params.select_DSP_rule[i])

if True:
    simulator = Run_Simulator()
    simulator.main("DQN","SQT") # dsp_rule = 개별 확인할 때만 사용하면 됨


    """
    m_ = [40, 32, 41, 28]
    q_ = [4,  1, 5,  6]
    i_ =[1  ,5 ,36,  102]
    
    """
# gantt chart 쑬 것인지
# 학습 방법, kpi목표
# 모든 디스패칭 룰 돌리기
