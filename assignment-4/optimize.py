from simulator import *
from numpy import arange


def optimize_round_robin(processes: List[Process], lower: int = 1, upper: int = 10, step_size: int = 1):
    with open('rr-op.txt', 'w') as f:
        # write header
        f.write('quantum avg.wait\n')

        for Q in range(lower, upper + step_size, step_size):
            sched, avg_wait = RR_scheduling(deepcopy(processes), time_quantum=Q)
            line = '%s %.5f\n' % (Q, avg_wait)
            f.write(line)
            print(line.strip())
    return


def optimize_sjf(processes: List[Process], lower: float = 0.0, upper: float = 1.0, step_size: float = 0.05):
    with open('sjf-op.txt', 'w') as f:
        # write header
        f.write('alpha avg.wait\n')

        for alpha in arange(lower, upper + step_size, step_size):
            sched, avg_wait = SJF_scheduling(deepcopy(processes), alpha=alpha)
            line = '%.3f %.5f\n' % (alpha, avg_wait)
            f.write(line)
            print(line.strip())

    return


if __name__ == '__main__':
    process_list = read_input('input.txt')
    # sort by arrival time
    process_list = sorted(process_list, key=lambda p: p.arrive_time)

    print("printing input ----")
    for process in process_list:
        print(process)

    print("simulating RR ----")
    optimize_round_robin(process_list, lower=1, upper=15, step_size=1)

    print("simulating SJF ----")
    optimize_sjf(process_list, lower=0.0, upper=1.0, step_size=0.02)
