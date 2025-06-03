import numpy as np
import time
class PoissonQueueSimulator:
    def __init__(self, arrival_rate, service_rate, num_visitors, num_queues, queue_policy='random'):
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        self.num_visitors = num_visitors
        self.num_queues = num_queues
        self.queue_policy = queue_policy
        self._round_robin_count = 0
        self.visitor_queue = [[] for _ in range(self.num_queues)] # (end time, total time)

    def simulate(self):
        arrival_times = np.random.exponential(scale = 1 / self.arrival_rate, size = self.num_visitors)
        process_times = np.random.exponential(scale = 1 / self.service_rate, size = self.num_visitors)
        max_queue_lengths = [0] * self.num_queues
        total_waiting_times = [0] * self.num_queues
        num_visitors_in_queue = [0] * self.num_queues
        visitors = []
        current_time = arrival_times[0]
        for visitor_id in range(self.num_visitors):
            queue_id = self._select_queue()
            # get the number of people actually queued in the selected queue
            queue_len = len(self.visitor_queue[queue_id])
            if queue_len == 0:
                start_time = current_time
            else:
                start_time = self.visitor_queue[queue_id][-1]['end_time']
            total_time = start_time - current_time + process_times[visitor_id]
            visitors.append({
                'visitor_id': visitor_id,
                'arrival_time': current_time,
                'process_time': process_times[visitor_id],
                'start_time': start_time,
                'end_time': current_time + total_time,
                'total_time': total_time,
                'queue_id': queue_id
            })
            self.visitor_queue[queue_id].append({
                'end_time': current_time + total_time,
                'total_time': total_time,
            })
            num_visitors_in_queue[queue_id] += 1
            total_waiting_times[queue_id] += total_time - process_times[visitor_id]
            if queue_len + 1 > max_queue_lengths[queue_id]:
                max_queue_lengths[queue_id] = queue_len + 1

            # update queues
            if visitor_id + 1 < self.num_visitors:
                current_time += arrival_times[visitor_id+1]
                for q in range(self.num_queues):
                    if len(self.visitor_queue[q]) > 0:
                        while self.visitor_queue[q][0]['end_time'] < current_time:
                            self.visitor_queue[q].pop(0)
                            if len(self.visitor_queue[q]) == 0:
                                break
        average_waiting_times = []
        for i in range(self.num_queues):
            if num_visitors_in_queue[i] > 0:
                average_waiting_times.append(total_waiting_times[i] / num_visitors_in_queue[i])
            else:
                average_waiting_times.append(0)
        return visitors, max_queue_lengths, average_waiting_times

    def _select_queue(self):
        if self.queue_policy == 'random':
            return np.random.randint(0, self.num_queues)
        elif self.queue_policy == 'round-robin':
            return self._round_robin()
        elif self.queue_policy == 'shortest-queue':
            return self._shortest_queue()
        else:
            raise ValueError(f"Invalid queue policy: {self.queue_policy}")

    def _round_robin(self):
        queue_id = self._round_robin_count % self.num_queues
        self._round_robin_count += 1
        return queue_id

    def _shortest_queue(self):
        minNbInQueue = self.num_visitors+1
        for queue_id in range(self.num_queues):
            if len(self.visitor_queue[queue_id]) < minNbInQueue:
                minQueues = [queue_id]
                minNbInQueue = len(self.visitor_queue[queue_id])
            elif len(self.visitor_queue[queue_id]) == minNbInQueue:
                minQueues.append(queue_id)
        return minQueues[np.random.randint(0, len(minQueues))]
        
def _run():
    simulator = PoissonQueueSimulator(arrival_rate, service_rate, num_visitors, num_queues, queue_policy)
    visitors, max_queue_lengths, average_waiting_times = simulator.simulate()
    print("Visitors:")
    print(f"Visitor ID;Arrival Time;Start Time;End Time;Process Time;Total Time;Queue ID")
    for visitor in visitors:
            print(f"{visitor['visitor_id']};{visitor['arrival_time']};"
                f"{visitor['start_time']};{visitor['end_time']};"
                f"{visitor['process_time']};{visitor['total_time']};"
                f"{visitor['queue_id']}")
    print("\nQueue Stats:")
    for queue_id, max_length in enumerate(max_queue_lengths):
            print(f"Queue ID: {queue_id}, Max Queue Length: {max_length}, Average Waiting Time: {average_waiting_times[queue_id]}")

# Example usage
seed = int(time.time())
np.random.seed(seed)
arrival_rate = 10  # average arrival rate of n visitors per time unit
service_rate = 1  # average service rate of n visitors per time unit
num_visitors = 20  # total number of visitors to simulate
num_queues = 8  # total number of queues
queue_policy = 'shortest-queue'  # queue selection policy: random, round-robin, shortest-queue

_run()
