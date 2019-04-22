from simulator import *
from numpy import arange


def optimize_round_robin(processes: List[Process], lower: int = 1, upper: int = 10, step_size: int = 1):
    results = dict()
    with open('rr-op.txt', 'w') as f:
        # write header
        f.write('quantum avg.wait\n')

        for Q in range(lower, upper + step_size, step_size):
            sched, avg_wait = RR_scheduling(deepcopy(processes), time_quantum=Q)
            results[Q] = avg_wait
            line = '%s %.5f\n' % (Q, avg_wait)
            f.write(line)
            # print(line.strip())
    return min(results, key=results.get)


def optimize_sjf(processes: List[Process], lower: float = 0.0, upper: float = 1.0, step_size: float = 0.05):
    results = dict()
    with open('sjf-op.txt', 'w') as f:
        # write header
        f.write('alpha avg.wait\n')

        for alpha in arange(lower, upper + step_size, step_size):
            sched, avg_wait = SJF_scheduling(deepcopy(processes), alpha=alpha)
            results[alpha] = avg_wait
            line = '%.3f %.5f\n' % (alpha, avg_wait)
            f.write(line)
            # print(line.strip())
    return min(results, key=results.get)


if __name__ == '__main__':
    process_list = read_input('input.txt')
    # sort by arrival time
    process_list = sorted(process_list, key=lambda p: p.arrive_time)

    print("printing input ----")
    for process in process_list:
        print(process)

    print("simulating RR ----")
    Q = optimize_round_robin(process_list, lower=1, upper=15, step_size=1)
    rr_sched, rr_wait = RR_scheduling(process_list, time_quantum=Q)
    write_output('rr-optimal-%s.txt' % Q, rr_sched, rr_wait)

    print("simulating SJF ----")
    alpha = optimize_sjf(process_list, lower=0.0, upper=1.0, step_size=0.02)
    sjf_sched, sjf_wait = SJF_scheduling(process_list, alpha=alpha)
    write_output('sjf-optimal-%s.txt' % alpha, sjf_sched, sjf_wait)
