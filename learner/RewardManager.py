class RewardManager:
    @classmethod
    def get_combination_reward_q_over_time_and_makespan(cls, machine, j_list, r_list, curr_time):
        """
        구성 reward : makespan 줄이는 reward * 0.5 + stocker에 대기 중인 q_time_over_time의 총합 * 0.5
        """
        r = 0
        reservation_time = r_list[machine].reservation_time
        last_work_finish_time = r_list[machine].last_work_finish_time
        total_idle = 0
        total_q_time_over = 0
        for resource in r_list:
            if r_list[resource].reservation_time < last_work_finish_time:
                total_idle += (last_work_finish_time - r_list[resource].reservation_time)
                r_list[resource].reservation_time = last_work_finish_time
        for job in j_list:  # job 이름과 operation이름 찾기
            if j_list[job].status == "WAIT":
                total_q_time_over += j_list[job].cal_q_time(curr_time)

        r -= (0.8 * (reservation_time - last_work_finish_time + total_idle) + 0.2 * total_q_time_over)
        return  r, r_list

    @classmethod
    def get_makespan_reward(cls, machine, j_list, r_list, curr_time):
        """
        구성 reward : makespan 줄이는 reward * 0.5 + stocker에 대기 중인 q_time_over_time의 총합 * 0.5
        """
        r = 0
        reservation_time = r_list[machine].reservation_time
        last_work_finish_time = r_list[machine].last_work_finish_time
        total_idle = 0
        total_q_time_over = 0
        for resource in r_list:
            if r_list[resource].reservation_time < last_work_finish_time:
                total_idle += (last_work_finish_time - r_list[resource].reservation_time)
                r_list[resource].reservation_time = last_work_finish_time
        for job in j_list:  # job 이름과 operation이름 찾기
            if j_list[job].status == "WAIT":
                total_q_time_over += j_list[job].cal_q_time(curr_time)

        r -= reservation_time - last_work_finish_time + total_idle
        return r, r_list

    @classmethod
    def get_reward(cls, reward_type,machine, j_list, r_list, curr_time):
        if reward_type == COMBINATION_Q_OVER_TIME_AND_MAKESPAN:
            r, r_list = cls.get_combination_reward_q_over_time_and_makespan(machine, j_list, r_list, curr_time)
        elif reward_type == MAKESPAN:
            r, r_list = cls.get_makespan_reward(machine,j_list,r_list,curr_time)
        return r, r_list

COMBINATION_Q_OVER_TIME_AND_MAKESPAN = "combination_reward_q_over_time_and_makespan"
MAKESPAN = "makespan"