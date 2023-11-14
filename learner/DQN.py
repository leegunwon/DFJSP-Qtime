from learner.Qnet import *
from learner.ReplayBuffer import *

import torch
import torch.nn.functional as F
import torch.optim as optim
import os
from simlator.Simulator import *

import logging
import random
from Parameters import *

class DQN:
    print("DQN on")

    @classmethod
    def train(cls, q, q_target, memory, optimizer):
        for i in range(10):
            s, a, r, s_prime, done_mask = memory.sample(Parameters.r_param["batch_size"])
            # q.number_of_time_list[a] += 1
            q_out = q(s)
            q_a = q_out.gather(1, a)
            max_q_prime = q_target(s_prime).max(1)[0].unsqueeze(1)
            # print(max_q_prime.shape)
            target = r + Parameters.r_param["gamma"] * max_q_prime * done_mask
            loss = F.smooth_l1_loss(q_a, target)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    @classmethod
    def main(cls):
        env = Simulator
        q = Qnet(Parameters.r_param["input_layer"], Parameters.r_param["output_layer"])
        q_target = Qnet(Parameters.r_param["input_layer"], Parameters.r_param["output_layer"])
        q_target.load_state_dict(q.state_dict())
        memory = ReplayBuffer(Parameters.r_param["buffer_limit"])
        print_interval = 1
        q_load = 20
        score = 0.0
        optimizer = optim.Adam(q.parameters(), lr=Parameters.r_param["learning_rate"])
        makespan_list = []
        q_over_time_list = []
        score_list = []
        save_directory = Parameters.save_parameter_directory + Parameters.simulation_time  # 디렉토리 경로를 지정합니다.
        if Parameters.param_down_on:
            os.makedirs(save_directory, exist_ok=True)  # 경로 없을 시 생성

        for n_epi in range(Parameters.r_param["episode"]):
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
                cls.train(q, q_target, memory, optimizer)
            makespan_list, q_over_time_list, score_list = cls.script_performance(env,n_epi,epsilon,memory, score, False, makespan_list, q_over_time_list, score_list)
            # 결과 및 파라미터 저장
            if Parameters.param_down_on:
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
            makespan_list, q_over_time_list, score_list = cls.script_performance(env,n_epi,epsilon,memory, score, True,makespan_list, q_over_time_list, score_list)
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
        return Flow_time, machine_util, util, makespan, score, makespan_list, q_over_time_list, score_list

    @classmethod
    def script_performance(cls, env, n_epi, epsilon,memory, score, type, makespan_list, q_over_time_list, score_list):
        Flow_time, machine_util, util, makespan, Tardiness_time, Lateness_time, T_max, q_time_true, q_time_false, q_job_t, q_job_f, q_over_time = env.performance_measure()

        output_string = "--------------------------------------------------\n" + \
                        f"flow time: {Flow_time}, util : {util:.3f}, makespan : {makespan}\n" + \
                        f"Tardiness: {Tardiness_time}, Lateness : {Lateness_time}, T_max : {T_max}\n" + \
                        f"q_true_op: {q_time_true}, q_false_op : {q_time_false}, q_true_job : {q_job_t}, q_false_job : {q_job_f}, q_over_time : {q_over_time}\n" + \
                        f"n_episode: {n_epi}, score : {score:.1f}, n_buffer : {memory.size()}, eps : {epsilon * 100:.1f}%"
        print(output_string)
        if type:
            makespan_list.append(makespan)
            q_over_time_list.append(q_over_time)
            score_list.append(score)
        if Parameters.log_on:
            logging.info(f'performance :{output_string}')
        return makespan_list, q_over_time_list, score_list

    @classmethod
    def plot_pareto(cls, makespan_list, q_over_time_list, score_list):
        pareto_optimal = []
        # makespan_list와 q_over_time_list를 결합하여 no_mk_q_list 생성
        no_mk_q_list = [[x, y, z, i] for i, (x, y, z) in enumerate(zip(makespan_list, q_over_time_list, score_list))]
        plt.plot([i for i in range(len(score_list))],score_list)
        plt.show()
        sort_no_mk_q_list = no_mk_q_list.sort(key=lambda x: x[2], reverse=True)
        print(sort_no_mk_q_list)
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








