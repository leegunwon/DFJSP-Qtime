
from Job import *
from Resource import *
class RewardManager:
    @classmethod
    def get_reward(cls, machine, j_list, r_list, curr_time):
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

        r -= (1 * (reservation_time - last_work_finish_time + total_idle) + 0 * total_q_time_over)
        return  r, r_list
