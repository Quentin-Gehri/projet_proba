import numpy as np
import time
import math
import matplotlib.pyplot as plt
from scipy.stats import norm

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
    '''
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
    '''
    moyenne = sum(average_waiting_times) / len(average_waiting_times)
    tmp = sorted(average_waiting_times)
    if (len(average_waiting_times) % 2 == 1):
        mediane = tmp[int(len(average_waiting_times) / 2)]
    else:
        mediane = (tmp[int(len(average_waiting_times) / 2)-1] + tmp[int(len(average_waiting_times) / 2)]) / 2
    variance = sum((x - moyenne) ** 2 for x in average_waiting_times) / len(average_waiting_times)
    # Ecart-type
    ecartType = math.sqrt(variance)

    print("Moyenne : ", moyenne)
    print("Mediane : ", mediane)
    print("Variance : ", round(variance, 2))
    print("Ecart-type : ", round(ecartType, 2))


def test_central_limit_theorem(num_runs=100):
    all_means = []
    for _ in range(num_runs):
        simulator = PoissonQueueSimulator(arrival_rate, service_rate, num_visitors, num_queues, queue_policy)
        _, _, avg_waits = simulator.simulate()
        overall_mean_wait = np.mean(avg_waits)
        all_means.append(overall_mean_wait)
    
    mean_of_means = np.mean(all_means)
    std_of_means = np.std(all_means)
    print(f"Moyennes des temps d'attentes moyens: {mean_of_means}")
    print(f"Écart-type des temps d'attente moyens: {std_of_means}")
        
    plt.hist(all_means, bins=20, edgecolor='black', alpha=0.7, density=True)
    x = np.linspace(min(all_means), max(all_means), 100)
    plt.plot(x, norm.pdf(x, mean_of_means, std_of_means), color='red', label='Courbe normale')
    plt.title(f"Distribution des temps d'attente pour {num_runs} simulations")
    plt.xlabel("Temps d'attente moyen (minutes)")
    plt.ylabel("Densité")
    plt.legend()
    plt.show()

def run_multiple_simulations_per_policy(n=100):
    import matplotlib.pyplot as plt
    import numpy as np
    import math

    policies = ['random', 'round-robin', 'shortest-queue']
    stats = {policy: {'means': [], 'medians': [], 'variances': [], 'std_devs': []} for policy in policies}

    for policy in policies:
        print(f"\nRunning simulations for policy: {policy}")
        for _ in range(n):
            simulator = PoissonQueueSimulator(arrival_rate, service_rate, num_visitors, num_queues, policy)
            _, _, average_waiting_times = simulator.simulate()

            moyenne = sum(average_waiting_times) / len(average_waiting_times)
            tmp = sorted(average_waiting_times)
            if len(average_waiting_times) % 2 == 1:
                mediane = tmp[len(average_waiting_times) // 2]
            else:
                mediane = (tmp[len(average_waiting_times) // 2 - 1] + tmp[len(average_waiting_times) // 2]) / 2
            variance = sum((x - moyenne) ** 2 for x in average_waiting_times) / len(average_waiting_times)
            ecartType = math.sqrt(variance)

            stats[policy]['means'].append(moyenne)
            stats[policy]['medians'].append(mediane)
            stats[policy]['variances'].append(variance)
            stats[policy]['std_devs'].append(ecartType)

    # Résumés agrégés
    aggregate = {
        'policy': policies,
        'mean_of_means': [np.mean(stats[p]['means']) for p in policies],
        'mean_of_medians': [np.mean(stats[p]['medians']) for p in policies],
        'mean_of_variances': [np.mean(stats[p]['variances']) for p in policies],
        'mean_of_std_devs': [np.mean(stats[p]['std_devs']) for p in policies]
    }

    # Liste des statistiques à afficher
    stat_names = ['mean_of_means', 'mean_of_medians', 'mean_of_variances', 'mean_of_std_devs']
    stat_labels = ['Moyenne', 'Médiane', 'Variance', 'Écart-type']
    y_labels = ['Moyenne d\'attente en minutes', 'Moyenne d\'attente en minutes', 'Moyenne d\'attente en minutes', 'Moyenne d\'attente en minutes']

    # Générer un graphique pour chaque statistique
    for stat_name, label, ylab in zip(stat_names, stat_labels, y_labels):
        plt.figure(figsize=(8, 5))
        values = aggregate[stat_name]
        
        # Couleurs douces pour chaque barre
        colors = ['lightcoral', 'sandybrown', 'palegreen', 'mediumaquamarine', 'plum', 'lightblue']
        bars = plt.bar(policies, values, color=colors[:len(policies)], edgecolor='black')
        
        # Affichage des valeurs au-dessus des barres
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f'{yval:.3f}', 
                    ha='center', va='bottom', fontsize=9)

        # Ligne horizontale à 4 minutes
        #plt.axhline(y=6.16, color='blue', linestyle='-', linewidth=1.5, label="Tolérance (6min16)")
        
        # Ajout d'une légende pour la ligne
        #plt.legend(loc='upper right', fontsize=9)
        
        plt.title(f"{label} des temps d'attente en minutes sur {n} simulations (5 caisses)")
        plt.ylabel(ylab)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.ylim(0, max(values) * 1.2)
        plt.show()




# Example usage
seed = int(time.time())
np.random.seed(seed)

# SEMAINE STAT
arrival_rate = 4.9  # average arrival rate of n visitors per time unit
service_rate = 1  # average service rate of n visitors per time unit
num_visitors = 3300  # total number of visitors to simulate
num_queues = 5  # total number of queues


#test_central_limit_theorem(8000)

# WEEKEND STAT
#arrival_rate = 10.3# average arrival rate of n visitors per time unit
#service_rate = 0.7 # average service rate of n visitors per time unit  
#num_visitors = 6500  # total number of visitors to simulate
#num_queues = 15  # total number of queues

queue_policy = 'round-robin'  # queue selection policy: random, round-robin, shortest-queue
print("\n\nPolitique: ", queue_policy)
_run()

queue_policy = 'random'
print("\n\nPolitique: ", queue_policy)
_run()

queue_policy = 'shortest-queue'
print("\n\nPolitique: ", queue_policy)
_run()

run_multiple_simulations_per_policy(1000)
