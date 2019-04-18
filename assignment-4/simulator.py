"""
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt


Darren Wee Zhe Yu
A0147609X
AY 2018/19 Semester 2
"""

from typing import Tuple, List, Dict, Set
from collections import deque
from copy import deepcopy


class Process:
    last_scheduled_time = 0

    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
        self.time_remaining = burst_time
        self.predicted_burst = None

    def __repr__(self):
        if self.predicted_burst is None:
            return '[id %d : arrival_time %d,  burst_time %d/%d]' % (self.id, self.arrive_time, self.time_remaining, self.burst_time)
        return '[id %d : arrival_time %d,  burst_time %d/%d(%s)]' % (self.id, self.arrive_time, self.time_remaining, self.burst_time, self.predicted_burst)


def FCFS_scheduling(process_list) -> Tuple[List[tuple], float]:
    # store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if current_time < process.arrive_time:
            current_time = process.arrive_time
        schedule.append((current_time, process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time / float(len(process_list))
    return schedule, average_waiting_time


"""
Input: process_list, time_quantum (Positive Integer)
Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
Output_2 : Average Waiting Time
"""


def receive_arrivals(is_completed, processes, current_time, queue):
    # add all arriving tasks to queue
    for p in processes:
        # process already registered
        if p in is_completed:
            continue

        if p.arrive_time <= current_time:
            queue.append(p)
            is_completed[p] = False
    return


def RR_scheduling(process_list: List[Process], time_quantum: int = 10) -> Tuple[List[tuple], float]:
    schedule = list()  # type: List[tuple]
    completed = dict()  # type: Dict[Process, bool]
    last_processed = dict()  # type: Dict[Process, int]
    waiting_time = 0

    done = 0
    first = process_list[0]
    work_queue = deque([first])
    t = first.arrive_time
    completed[first] = False

    while True:
        if done == len(process_list):
            break

        # process everything in queue
        # print('\nt = %3s; queue = %s' % (t, work_queue))

        try:
            current_process = work_queue.popleft()  # type: Process
        except IndexError:
            # no work to do and no processes are arriving
            t += 1
            receive_arrivals(completed, process_list, t, work_queue)
            continue
        # print('t = %3s: scheduling %s' % (t, current_process))
        schedule.append((t, current_process.id))

        # update waiting time between end of last processing period and start of this processing period
        if current_process in last_processed:
            waiting_time += t - last_processed[current_process]
        else:
            waiting_time += t - current_process.arrive_time

        if current_process.time_remaining > time_quantum:
            t += time_quantum
            current_process.time_remaining -= time_quantum
        else:
            t += current_process.time_remaining
            current_process.time_remaining = 0
            completed[current_process] = True
            done += 1
            # print('t = %3s: completed %s' % (t, current_process))

        # track timestamp of last processing (end of time slice)
        last_processed[current_process] = t

        receive_arrivals(completed, process_list, t, work_queue)

        if not completed[current_process]:
            work_queue.append(current_process)
    return schedule, waiting_time / len(process_list)


def SRTF_scheduling(process_list: List[Process]) -> Tuple[List[tuple], float]:
    schedule = list()  # type: List[tuple]
    completed = dict()  # type: Dict[Process, bool]
    work_queue = deque([])
    waiting_time = 0
    done = 0
    t = 0

    previous_process = None
    while True:
        if done == len(process_list):
            break

        receive_arrivals(completed, process_list, t, work_queue)

        # sort by remaining time, then arrival time, then burst time and id
        work_queue = sorted(work_queue, key=lambda p: (p.time_remaining, p.arrive_time, p.burst_time, p.id))
        work_queue = deque(work_queue)
        # print('t = %3s: %s' % (t, work_queue))

        # get the highest priority process to work on
        try:
            current_process = work_queue.popleft()  # type: Process

            # update waiting time
            waiting_time += len(work_queue)
        except IndexError:
            # no work to do and no processes are arriving
            t += 1
            receive_arrivals(completed, process_list, t, work_queue)
            continue

        # check if pre-emption/context switch is needed
        if current_process is not previous_process:
            # record new schedule
            schedule.append((t, current_process.id))

        current_process.time_remaining -= 1

        previous_process = current_process
        t += 1

        if current_process.time_remaining == 0:
            done += 1
            continue

        # add current process back to queue if not done
        work_queue.append(current_process)

    return schedule, waiting_time / len(process_list)


def SJF_scheduling(process_list: List[Process], alpha: float = 0.5, initial_guess: int = 5) -> Tuple[List[tuple], float]:
    schedule = list()  # type: List[tuple]
    completed = dict()  # type: Dict[Process, bool]
    work_queue = deque([])
    waiting_time = 0
    done = 0
    t = 0

    # burst time history on a per-pid basis
    burst_history = dict()  # type: Dict[int, List[int]]
    prediction_history = dict()  # type: Dict[int, List[float]]

    # populate initial guesses for burst
    for p in process_list:
        prediction_history[p.id] = [initial_guess]
        # affix burst history to 0 since the process has never run before
        burst_history[p.id] = list()

    encountered_pids = set()  # type: Set[int]
    while True:
        if done == len(process_list):
            break

        receive_arrivals(completed, process_list, t, work_queue)

        # compute burst predictions for all processes in queue
        for p in work_queue:
            # populate initial predictions
            if p.id not in encountered_pids:
                p.predicted_burst = initial_guess
                encountered_pids.add(p.id)

            # compute predictions for subsequent attempts thereafter
            if p.predicted_burst is None:
                prediction = alpha * burst_history[p.id][-1] + (1 - alpha) * prediction_history[p.id][-1]
                # print('pred history  = %s' % prediction_history[p.id])
                # print('burst history = %s' % burst_history[p.id])
                # print('predicted burst is %s' % prediction)
                prediction_history[p.id].append(prediction)
                p.predicted_burst = prediction

        # sort by predicted burst time, then arrival time, then pid
        work_queue = sorted(work_queue, key=lambda proc: (proc.predicted_burst, proc.arrive_time, proc.id))
        work_queue = deque(work_queue)
        # print('t = %3s: %s' % (t, work_queue))

        # get the highest priority process to work on
        try:
            current_process = work_queue.popleft()  # type: Process
            # print(current_process)
        except IndexError:
            # no work to do and no processes are arriving
            t += 1
            receive_arrivals(completed, process_list, t, work_queue)
            continue

        # schedule shortest predicted job w/o preemption
        schedule.append((t, current_process.id))

        # compute waiting time for the newly scheduled process
        waiting_time += t - current_process.arrive_time

        # advance scheduler timestamp
        t += current_process.burst_time
        burst_history[current_process.id].append(current_process.burst_time)

        done += 1

    return schedule, waiting_time / len(process_list)


def read_input(filename: str) -> List[Process]:
    result = []
    with open(filename) as f:
        for line in f:
            array = line.split()
            if len(array) != 3:
                print("wrong input format")
                exit()
            result.append(Process(int(array[0]), int(array[1]), int(array[2])))
    return result


def write_output(file_name: str, schedule: List[Tuple], avg_waiting_time: float):
    with open(file_name, 'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n' % avg_waiting_time)


def main(input_file: str = 'input.txt'):
    process_list = read_input(input_file)
    # sort by arrival time
    process_list = sorted(process_list, key=lambda p: p.arrive_time)

    print("printing input ----")
    for process in process_list:
        print(process)

    print("simulating FCFS ----")
    fcfs_schedule, fcfs_avg_waiting_time = FCFS_scheduling(deepcopy(process_list))
    write_output('FCFS.txt', fcfs_schedule, fcfs_avg_waiting_time)

    print("simulating RR ----")
    rr_schedule, rr_avg_waiting_time = RR_scheduling(deepcopy(process_list), time_quantum=2)
    write_output('RR.txt', rr_schedule, rr_avg_waiting_time)

    print("simulating SRTF ----")
    srtf_schedule, srtf_avg_waiting_time = SRTF_scheduling(deepcopy(process_list))
    write_output('SRTF.txt', srtf_schedule, srtf_avg_waiting_time)

    print("simulating SJF ----")
    sjf_schedule, sjf_avg_waiting_time = SJF_scheduling(process_list, alpha=0.5)
    write_output('SJF.txt', sjf_schedule, sjf_avg_waiting_time)


if __name__ == '__main__':
    main()
