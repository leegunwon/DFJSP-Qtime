from Qnet import *
from ReplayBuffer import *

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import os
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

    def main(self, time_to_string):
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
        save_directory = '/Users/shin/DFJSP-Qtime/params_data/' + time_to_string  # 디렉토리 경로를 지정합니다.
        os.makedirs(save_directory, exist_ok=True)  # 경로 없을 시 생성

        for n_epi in range(self.r_param["episode"]):
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
                file_name = str(n_epi) + "param.pt"
                file_path = os.path.join(save_directory, file_name)
                torch.save(params, file_path)


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
        Flow_time, machine_util, util, makespan, tardiness, lateness, t_max,q_time_true,q_time_false,q_job_t, q_job_f, q_time = env.performance_measure()
        #env.gantt_chart()
        return Flow_time, machine_util, util, makespan, score, makespan_list, q_over_time_list



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

    def plot_pareto(self, makespan_list, q_over_time_list):
        pareto_optimal = []

        # makespan_list와 q_over_time_list를 결합하여 no_mk_q_list 생성
        no_mk_q_list = [[x, y, i] for i, (x, y) in enumerate(zip(makespan_list, q_over_time_list))]

        for i, point in enumerate(no_mk_q_list):
            is_pareto_optimal = True

            for existing_point in pareto_optimal[:]:
                if existing_point[0] <= point[0] and existing_point[1] <= point[1]:
                    is_pareto_optimal = False
                elif point[0] <= existing_point[0] and point[1] <= existing_point[1]:
                    pareto_optimal.remove(existing_point)

            if is_pareto_optimal:
                pareto_optimal.append(point)

        # 파레토 최적해 산점도 그리기
        makespan_values = [point[0] for point in pareto_optimal]
        q_values = [point[1] for point in pareto_optimal]

        plt.scatter(makespan_values, q_values)
        plt.xlabel('Makespan')
        plt.ylabel('Q over time')
        plt.title('Pareto Optimal Solutions')
        plt.show()
        print(pareto_optimal)









