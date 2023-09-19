from Qnet import *
from ReplayBuffer import *

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

import gym
import collections
import random
from simulator_DFJSP import *

class DQN:
    def __init__(self,params, r_param):
        print("DQN on")
        self.params = params
        self.r_param =r_param

    def train(self, q, q_target, memory, optimizer):
        for i in range(10):
            s, a, r, s_prime, done_mask = memory.sample(self.r_param["batch_size"])
            # q.number_of_time_list[a] += 1
            q_out = q(s)
            q_a = q_out.gather(1, a)
            max_q_prime = q_target(s_prime).max(1)[0].unsqueeze(1)
            # print(max_q_prime.shape)
            target = r + self.r_param["gamma"] * max_q_prime * done_mask
            loss = F.smooth_l1_loss(q_a, target)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    def main(self):
        env = FJSP_simulator(self.params["p_data"], self.params["s_data"], self.params["q_data"], self.params["rd_data"])
        q = Qnet(self.r_param["input_layer"], self.r_param["output_layer"])
        q_target = Qnet(self.r_param["input_layer"], self.r_param["output_layer"])
        q_target.load_state_dict(q.state_dict())
        memory = ReplayBuffer(self.r_param["buffer_limit"])
        print_interval = 1
        q_load = 10
        score = 0.0
        optimizer = optim.Adam(q.parameters(), lr=self.r_param["learning_rate"])
        makespan_list = []
        q_over_time_list = []

        for n_epi in range(1000):
            # 여기는 sample_action 구간
            epsilon = max(0.01, 0.08 - 0.02 * (n_epi / 200))
            s = env.reset()
            done = False
            score = 0.0
            while not done:
                a = q.sample_action(torch.from_numpy(s).float(), epsilon)

                s_prime, r, done = env.step(a)
                done_mask = 0.0 if done else 1.0
                if done == False:
                    memory.put((s, a, r, s_prime, done_mask))
                    s = s_prime

                    score += r
                if done:
                    break

            # 학습구간
            if memory.size() > 1000:
                self.train(q, q_target, memory, optimizer)
            makespan_list, q_over_time_list = self.script_performance(env,n_epi,epsilon,memory, score, False, makespan_list, q_over_time_list)
            # 결과 및 파라미터 저장
            if n_epi % print_interval == 0 and n_epi != 0:
                params = q.state_dict()
                param_name = str(n_epi) + "nomorspt.pt"
                torch.save(params, param_name)


            # 여기는 select_action 구간
            s = env.reset()
            done = False
            score = 0.0
            while not done:
                a, a_list = q.select_action(torch.from_numpy(s).float(), epsilon)
                s_prime, r, done = env.step(a)
                s = s_prime
                score += r
                if done:
                    break
            makespan_list, q_over_time_list = self.script_performance(env,n_epi,epsilon,memory, score, True,makespan_list, q_over_time_list)

            if n_epi % q_load == 0 and n_epi != 0:
                q_target.load_state_dict(q.state_dict())

        s = env.reset()
        done = False
        score = 0.0
        while not done:
            a, a_list = q.select_action(torch.from_numpy(s).float(), epsilon)
            # print(a_list)
            # print(a)
            s_prime, r, done = env.step(a)
            # print(r)
            s = s_prime
            score += r
            if done:
                break
        Flow_time, machine_util, util, makespan, Tardiness_time, Lateness_time, T_max, q_time_true, q_time_false, q_job_t, q_job_f = env.performance_measure()
        env.gannt_chart()
        return Flow_time, machine_util, util, makespan, score



    def script_performance(self, env, n_epi, epsilon,memory, score, type, makespan_list, q_over_time_list):
        Flow_time, machine_util, util, makespan, Tardiness_time, Lateness_time, T_max, q_time_true, q_time_false, q_job_t, q_job_f, q_over_time = env.performance_measure()

        print("--------------------------------------------------")
        print("flow time: {}, util : {:.3f}, makespan : {}".format(Flow_time, util, makespan))
        print("Tardiness: {}, Lateness : {}, T_max : {}".format(Tardiness_time, Lateness_time, T_max))
        print("q_true_op: {}, q_false_op : {}, q_true_job : {}, , q_false_job : {} , q_over_time : {}".format(
            q_time_true, q_time_false, q_job_t, q_job_f, q_over_time))
        print(
            "n_episode: {}, score : {:.1f}, n_buffer : {}, eps : {:.1f}%".format(n_epi, score,
                                                                                 memory.size(), epsilon * 100))
        if type:
            makespan_list.append(makespan)
            q_over_time_list.append(q_over_time)

        return makespan_list, q_over_time_list


