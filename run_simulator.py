from DQN import *
from simulator_DFJSP import *
from Parameter import *

class Run_Simulator:
    def __init__(self, dsp_rule):
        print("simulator on")
        self.params = Parameters()
        self.DQN = DQN(self.params.data, self.params.r_param)
        self.simulator = FJSP_simulator(self.params.data["p_data"],self.params.data["s_data"],
                                        self.params.data["q_data"],self.params.data["rd_data"],self.params.select_DSP_rule[dsp_rule])
    def main(self, mode):
        if mode == "DQN":
            self.DQN.main()
        elif mode == "DSP_run":
            self.simulator.run()
if True:
    simulator = Run_Simulator("SPT")
    simulator.main("DQN")
