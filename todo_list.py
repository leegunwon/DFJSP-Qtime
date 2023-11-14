#todo
"""
todo :
    1. 스케줄링 종료 후 lot의 흐름이나, machine의 가동 방향을 DB에 저장하고 확인
    2. DSP rule 사용 시 어떤 작업의 어떤 공정이 어떤 기계에서 몇 시간에 걸쳐 사용 됐는지를 구간 별로 한 번에 정리해서 log로 남기기
    3. 코드 간결화 및 정리
    4. 현재 format을 db에 저장하도록 하는 파이썬 파일 작성 -> csv를 4개 넣거나.. 1개 넣었을 때 결과
    5. 강화학습 사용 시 reset 부분 처리 -> machine의 상태를 롤백시키거나, job의 상태를 롤백 시키는 작업 필요
    6. 파라미터 정리 및 분류
    7. job -> lot로 변경

"""
import random
import copy

def crossover_operator_MOX(mom, dad):
    mom_ch = mom[0]
    dad_ch = dad[0]

    from_mom_to_off_index = []
    from_dad_to_off_index = []

    mom_ch_jobs = []
    dad_ch_jobs = []

    mom_ch_cp = copy.deepcopy(mom_ch)
    dad_ch_cp = copy.deepcopy(dad_ch)
    point1 = 5
    point2 = 9
    for point in range(point1, point2):
        for j in range(len(dad_ch)):
            if mom_ch[point] == dad_ch_cp[j]:
                dad_ch_cp[j] = -1
                from_mom_to_off_index.append(j)
                mom_ch_jobs.append(mom_ch[point])
                break
        for k in range(len(dad_ch)):
            if dad_ch[point] == mom_ch_cp[k]:
                mom_ch_cp[k] = -1
                from_dad_to_off_index.append(k)
                dad_ch_jobs.append(dad_ch[point])
                break
    offspring_from_dad = copy.deepcopy(dad_ch)
    offspring_from_mom = copy.deepcopy(mom_ch)

    from_mom_to_off_index.sort(reverse=False)
    from_dad_to_off_index.sort(reverse=False)

    print(from_dad_to_off_index)
    print(from_mom_to_off_index)
    print(dad_ch_jobs)
    print(mom_ch_jobs)


    for i in range(len(from_dad_to_off_index)):
        offspring_from_dad[from_mom_to_off_index[i]] = mom_ch_jobs[i]
        offspring_from_mom[from_dad_to_off_index[i]] = dad_ch_jobs[i]

    return offspring_from_dad, offspring_from_mom

a = [[2,4,4,3,2,1,1,1,2,2,3,4],1]
b = [[2,4,2,2,1,4,3,4,3,1,2,1],2]

print(a)
print(b)

a1, a2 = crossover_operator_MOX(a, b)
print(a1)
print(a2)