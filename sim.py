import random, math
import matplotlib.pyplot as plt

from enum import Enum

class Policy(Enum):
    GREEDY = 1
    PATIENT = 2
    PATIENT_ALPHA = 3

class Agent:
    _id_counter = 0
    def __init__(self, arrival_time, deadline, agent_type, patience_cost=0.0):
        self.id = Agent._id_counter
        Agent._id_counter += 1
        self.arrival_time = arrival_time
        self.deadline = deadline
        self.agent_type = agent_type
        self.patience_cost = patience_cost
        self.matched = False
        self.match_time = None
        self.partner_id = None
    def is_expired(self, t): return t >= self.deadline

def are_compatible(a, b, p_easy_easy=0.9, p_easy_hard=0.4, p_hard_hard=0.1):
    if a.agent_type == b.agent_type == "easy": return random.random() < p_easy_easy
    if a.agent_type == b.agent_type == "hard": return random.random() < p_hard_hard
    return random.random() < p_easy_hard

# safer matching
def greedy_match(waiting, t):
    matched_pairs = []
    unmatched = []
    used = set()
    for i, a in enumerate(waiting):
        if i in used: continue
        found = False
        for j, b in enumerate(waiting):
            if j in used or i == j: continue
            if are_compatible(a, b):
                a.matched = b.matched = True
                a.match_time = b.match_time = t
                a.partner_id, b.partner_id = b.id, a.id
                used.add(i); used.add(j)
                matched_pairs.append((a,b,t))
                found = True
                break
        if not found: unmatched.append(a)
    return matched_pairs, [a for i,a in enumerate(waiting) if i not in used]

def patient_match(waiting, t):
    expiring = [a for a in waiting if a.deadline <= t]
    stay = [a for a in waiting if a.deadline > t]
    pairs, _ = greedy_match(expiring, t)
    matched_ids = {a.id for (a,b,_) in pairs} | {b.id for (a,b,_) in pairs}
    # agents whose deadline reached but unmatched leave
    remaining = stay + [a for a in expiring if a.id in matched_ids]
    return pairs, remaining

def patient_alpha_match(waiting, t, alpha=0.3):
    if random.random() < alpha:
        return greedy_match(waiting, t)
    else:
        return patient_match(waiting, t)

def poisson_arrivals(rate, T):
    t, arrivals = 0, []
    while t < T:
        t += random.expovariate(rate)
        if t <= T: arrivals.append(t)
    return arrivals

def run_simulation(T=100, arrival_rate=1.0, easy_fraction=0.7,
                   avg_deadline=10.0, policy=Policy.GREEDY,
                   alpha=0.3, waiting_cost_per_unit=0.05):
    arrivals = poisson_arrivals(arrival_rate, T)
    arrivals.sort()
    waiting, all_agents, matches = [], [], []
    idx, current_time = 0, 0
    while (current_time <= T or idx < len(arrivals)):
        if idx < len(arrivals): current_time = arrivals[idx]
        else: current_time += 1
        # add new agents
        while idx < len(arrivals) and abs(arrivals[idx]-current_time) < 1e-9:
            agent_type = "easy" if random.random() < easy_fraction else "hard"
            deadline = current_time + random.expovariate(1.0/avg_deadline)
            cost = waiting_cost_per_unit*random.uniform(0.5,1.5)
            a = Agent(current_time, deadline, agent_type, cost)
            waiting.append(a); all_agents.append(a); idx += 1
        # remove expired
        waiting = [a for a in waiting if not a.is_expired(current_time)]
        # match according to policy
        if policy == Policy.GREEDY:
            pairs, waiting = greedy_match(waiting, current_time)
        elif policy == Policy.PATIENT:
            pairs, waiting = patient_match(waiting, current_time)
        else:
            pairs, waiting = patient_alpha_match(waiting, current_time, alpha)
        matches.extend(pairs)
        # safety break
        if current_time > T*2: break
    # compute welfare
    matched = [a for a in all_agents if a.matched]
    unmatched = [a for a in all_agents if not a.matched]
    welfare = sum(1 - a.patience_cost*(a.match_time-a.arrival_time)
                  for a in matched)
    avg_wait = sum(a.match_time - a.arrival_time for a in matched)/len(matched) if matched else 0
    return {
        "match_rate": len(matched)/len(all_agents),
        "avg_wait": avg_wait,
        "welfare": welfare,
        "matched": len(matched),
        "unmatched": len(unmatched),
        "total": len(all_agents)
    }

if __name__ == "__main__":
    random.seed(0)
    horizon = 200
    print("=== Homogeneous market (easy=0.9) ===")
    for policy in [Policy.GREEDY, Policy.PATIENT, Policy.PATIENT_ALPHA]:
        res = run_simulation(T=horizon, easy_fraction=0.9, policy=policy)
        print(policy.name, res)

    print("\n=== Imbalanced market (easy=0.3) ===")
    for policy in [Policy.GREEDY, Policy.PATIENT, Policy.PATIENT_ALPHA]:
        res = run_simulation(T=horizon, easy_fraction=0.3, policy=policy)
        print(policy.name, res)
        
def plot_alpha_sweep(easy_fraction, T=200):
    alphas = [i / 10 for i in range(0, 11)]
    match_rates, welfares = [], []

    for a in alphas:
        res = run_simulation(T=T, easy_fraction=easy_fraction,
                             policy=Policy.PATIENT_ALPHA, alpha=a)
        match_rates.append(res["match_rate"])
        welfares.append(res["welfare"])

    plt.figure(figsize=(10,4))
    plt.subplot(1,2,1)
    plt.plot(alphas, match_rates, marker='o')
    plt.title(f"Match Rate vs Alpha (easy_fraction={easy_fraction})")
    plt.xlabel("Alpha (Greediness)")
    plt.ylabel("Match Rate")

    plt.subplot(1,2,2)
    plt.plot(alphas, welfares, marker='o', color='orange')
    plt.title(f"Welfare vs Alpha (easy_fraction={easy_fraction})")
    plt.xlabel("Alpha (Greediness)")
    plt.ylabel("Welfare")

    plt.tight_layout()
    plt.show()

# Run sweeps for both markets
plot_alpha_sweep(easy_fraction=0.9)  # homogeneous
plot_alpha_sweep(easy_fraction=0.3)  # imbalanced


