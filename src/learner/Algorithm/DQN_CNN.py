from src.learner.common.ReplayBuffer import *

from src.simulator.Simulator import *

from src.common.Parameters import *

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

import random

import matplotlib.pyplot as plt

class CNN(nn.Module):
    def __init__(self, input_layer, output_layer):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(
            in_channels=1,
            out_channels=4,
            kernel_size=(2, 2),
            stride=(1, 1),
            padding=(1, 1),
        )
        self.conv2 = nn.Conv2d(
            in_channels=4,
            out_channels=8,
            kernel_size=(2, 2),
            stride=(1, 1),
            padding=(1, 1),
        )

        self.pool = nn.AvgPool2d(kernel_size=(2, 2), stride=(1, 1))  # 맥스 풀링 레이어 추가

        self.fc1 = nn.Linear(168, 84)
        # self.fc2 = nn.Linear(84, 42)
        self.fc3 = nn.Linear(84, output_layer)

    def forward(self, x):
        shape = 1
        if len(x.shape) == 4:
            shape = x.shape[0]
        x = F.relu(self.conv1(x))
        # x = F.relu(self.conv2(x))
        # x = self.pool(x)  # 맥스 풀링 레이어 추가
        x = x.reshape(shape, -1)
        x = F.relu(self.fc1(x))
        # x = F.relu(self.fc2(x))
        x = self.fc3(x)

        return x

    def sample_action(self, obs, epsilon):
        out = self.forward(obs)
        coin = random.random()
        if coin < epsilon:
            return random.randint(0, 1)
        else:
            return out.argmax().item()

    def select_action(self, obs, epsilon):
        out = self.forward(obs)
        return out.argmax().item(), out


class DQN_CNN:
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

        q = Qnet(Parameters.r_param["input_layer"], Parameters.r_param["output_layer"])
        q_target = Qnet(Parameters.r_param["input_layer"], Parameters.r_param["output_layer"])
        q_target.load_state_dict(q.state_dict())
        memory = ReplayBuffer(Parameters.r_param["buffer_limit"])
        score = 0.0
        optimizer = optim.Adam(q.parameters(), lr=Parameters.r_param["learning_rate"])

        makespan_list = []
        q_over_time_list = []
        score_list = []
        util_list = []
        score_list2 = []
        save_directory = Parameters.save_parameter_directory + Parameters.simulation_time  # 디렉토리 경로를 지정합니다.

        if Parameters.param_down_on:
            os.makedirs(save_directory, exist_ok=True)  # 경로 없을 시 생성

        for n_epi in range(Parameters.r_param["episode"]):
            for dataid in Parameters.db_data:
                epsilon = max(0.01, 0.8 - 0.001 * n_epi)
                s = Simulator.reset(dataid)
                done = False
                score = 0.0
                while not done:
                    a = q.sample_action(torch.from_numpy(s).float(), epsilon)
                    s_prime, r, done = Simulator.step(a)
                    done_mask = 0.0 if done else 1.0
                    if done == False:
                        memory.put((s, a, r, s_prime, done_mask))
                        s = s_prime
                        score += r
                    if done:
                        break
                print(dataid)
                makespan_list, q_over_time_list, score_list = cls.script_performance(env, n_epi, epsilon, memory, score,
                                                                                     False, makespan_list,
                                                                                     q_over_time_list,
                                                                                     score_list)
                # env.gantt_chart()

            # 학습구간
            if memory.size() > 1000:
                cls.train(q, q_target, memory, optimizer)

            # 결과 및 파라미터 저장
            if Parameters.param_down_on:
                params = q.state_dict()
                file_name = str(n_epi) + "param.pt"
                file_path = os.path.join(save_directory, file_name)
                torch.save(params, file_path)

        x = [i for i in range(len(util_list))]
        plt.plot(x, util_list)
        plt.plot(x, score_list2)
        plt.show()
        print("학습이 종료되었습니다")
        return Flow_time, machine_util, util, makespan, score, makespan_list, q_over_time_list, score_list

    @classmethod
    def get_result(cls, parameter, dataSets):
        env = Simulator
        memory = ReplayBuffer(Parameters.r_param["buffer_limit"])
        q = Qnet(Parameters.r_param["input_layer"], Parameters.r_param["output_layer"])
        params = torch.load(parameter)
        q.load_state_dict(params)
        q.eval()
        for data_id in dataSets:
            s = env.reset(data_id)
            done = False
            score = 0.0
            while not done:
                epsilon = 1
                a, a_list = q.select_action(torch.from_numpy(s).float(), epsilon)
                s_prime, r, done = env.step(a)
                s = s_prime
                score += r
                if done:
                    break
            Flow_time, machine_util, util, makespan, tardiness, lateness, t_max, q_time_true, q_time_false, q_job_t, q_job_f, q_time, rtf = env.performance_measure()
            env.gantt_chart()
            print(f"dataset: {data_id}")
            print("util:", util)
            print("Tardiness:", tardiness)
            if Parameters.log_on:
                logging.info(f"dataset: {data_id}")
                logging.info(f"util: {util}")
            print("평가가 종료되었습니다.")

    @classmethod
    def get_evaluate(cls, checkpoint_path, number_of_checkpoint, datasets):
        env = Simulator
        file_list = [f for f in os.listdir(checkpoint_path) if os.path.isfile(os.path.join(checkpoint_path, f))]
        interver = len(file_list) // number_of_checkpoint
        check_point_list = [i for i in range(1, len(file_list)) if i % interver == 0]
        check_point_list.append(len(file_list) - 1)

        memory = ReplayBuffer(Parameters.r_param["buffer_limit"])
        q = Qnet(Parameters.r_param["input_layer"], Parameters.r_param["output_layer"])
        mean_reward_by_checkpoint = {}
        max_reward_by_checkpoint = {}
        for check_point_number in check_point_list:
            check_point = f"{checkpoint_path}/{check_point_number}param.pt"
            params = torch.load(check_point)
            q.load_state_dict(params)
            q.eval()
            reward_list = []
            for dataset in datasets:
                s = env.reset(dataset)
                done = False
                score = 0.0
                while not done:
                    epsilon = 1
                    a, a_list = q.select_action(torch.from_numpy(s).float(), epsilon)
                    # print(a_list)
                    # print(a)
                    s_prime, r, done = env.step(a)
                    # print(r)
                    s = s_prime
                    score += r
                    if done:
                        break
                Flow_time, machine_util, util, makespan, tardiness, lateness, t_max, q_time_true, q_time_false, q_job_t, q_job_f, q_time, rtf = env.performance_measure()
                reward_list.append(score)
                if Parameters.log_on:
                    logging.info(f"checkpoint: {check_point_number}")
                    logging.info(f"dataset: {dataset}")
                    logging.info(f"score:{score}")
                print(f"checkpoint: {check_point_number}")
                print(f"dataset: {dataset}")
                print(f"score:{score}")

            mean_reward_by_checkpoint[check_point_number] = sum(reward_list) / len(reward_list)
            max_reward_by_checkpoint[check_point_number] = max(reward_list)

        max_check_point = max(max_reward_by_checkpoint.items(), key=lambda x: x[1])[0]
        mean_check_point = max(mean_reward_by_checkpoint.items(), key=lambda x: x[1])[0]

        if Parameters.log_on:
            logging.info(f"max_checkpoint: {max_check_point}")
            logging.info(f"mean_checkpoint: {mean_check_point}")
        print(f"max_checkpoint: {max_check_point}")
        print(f"mean_checkpoint: {mean_check_point}")
        print("평가가 종료되었습니다.")

    @classmethod
    def script_performance(cls, env, n_epi, epsilon, memory, score, type, makespan_list, q_over_time_list, score_list):
        Flow_time, machine_util, util, makespan, Tardiness_time, Lateness_time, T_max, q_time_true, q_time_false, q_job_t, q_job_f, q_over_time, rtf = env.performance_measure()

        output_string = "--------------------------------------------------\n" + \
                        f"flow time: {Flow_time}, util : {util:.3f}, makespan : {makespan}, rtf: {rtf}\n" + \
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
