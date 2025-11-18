import random, math
import numpy as np
import matplotlib.pyplot as plt

from enum import Enum
from collections import defaultdict

class Policy(Enum):
    GREEDY = 1
    PATIENT = 2
    PATIENT_ALPHA = 3
    URGENCY_AWARE = 4  # prioritize high-urgency agents
    ADAPTIVE_ALPHA = 5  # adjust alpha based on pool urgency

class Agent:
    _id_counter = 0
    def __init__(self, arrival_time, deadline, agent_type, patience_cost=0.0, urgency_signal=None):
        self.id = Agent._id_counter
        Agent._id_counter += 1
        self.arrival_time = arrival_time
        self.deadline = deadline
        self.agent_type = agent_type
        self.patience_cost = patience_cost
        self.matched = False
        self.match_time = None
        self.partner_id = None
        # Urgency signal: observable indicator correlated with true deadline
        self.urgency_signal = urgency_signal if urgency_signal is not None else deadline - arrival_time
    
    def is_expired(self, t): return t >= self.deadline
    
    def time_until_deadline(self, t): return max(0, self.deadline - t)

def are_compatible(a, b, p_easy_easy=0.9, p_easy_hard=0.4, p_hard_hard=0.1, 
                   compatibility_matrix=None):
    """Check if two agents are compatible.
    
    Args:
        a, b: Agent objects
        p_easy_easy, p_easy_hard, p_hard_hard: default 2-type probabilities
        compatibility_matrix: dict mapping (type_a, type_b) -> probability
    """
    if compatibility_matrix is not None:
        # Use custom compatibility matrix
        key = (a.agent_type, b.agent_type)
        # Matrix should be symmetric
        prob = compatibility_matrix.get(key, compatibility_matrix.get((b.agent_type, a.agent_type), 0.0))
        return random.random() < prob
    
    # Default 2-type behavior
    if a.agent_type == b.agent_type == "easy": return random.random() < p_easy_easy
    if a.agent_type == b.agent_type == "hard": return random.random() < p_hard_hard
    return random.random() < p_easy_hard

def create_compatibility_matrix(n_types, structure='uniform', intra_prob=0.8, inter_prob=0.2):
    """Create a compatibility matrix for n types.
    
    Args:
        n_types: number of agent types
        structure: 'uniform', 'clustered', 'core_periphery'
        intra_prob: probability for within-group matches
        inter_prob: probability for across-group matches
    
    Returns:
        dict mapping (type_i, type_j) -> probability
    """
    matrix = {}
    types = [f"type_{i}" for i in range(n_types)]
    
    if structure == 'uniform':
        # All pairs have same probability
        for i in range(n_types):
            for j in range(i, n_types):
                prob = intra_prob if i == j else inter_prob
                matrix[(types[i], types[j])] = prob
                matrix[(types[j], types[i])] = prob
    
    elif structure == 'clustered':
        # Divide types into clusters; high within-cluster, low across-cluster
        cluster_size = max(2, n_types // 2)
        for i in range(n_types):
            for j in range(i, n_types):
                # Same cluster if floor(i/cluster_size) == floor(j/cluster_size)
                same_cluster = (i // cluster_size) == (j // cluster_size)
                prob = intra_prob if same_cluster else inter_prob * 0.5
                matrix[(types[i], types[j])] = prob
                matrix[(types[j], types[i])] = prob
    
    elif structure == 'core_periphery':
        # First type is "core" (universal donor), others are periphery
        core_type = types[0]
        for i in range(n_types):
            for j in range(i, n_types):
                if i == 0 or j == 0:  # involves core
                    prob = intra_prob
                elif i == j:
                    prob = inter_prob
                else:
                    prob = inter_prob * 0.3  # periphery-periphery is hard
                matrix[(types[i], types[j])] = prob
                matrix[(types[j], types[i])] = prob
    
    return matrix, types

def sample_agent_type(types, distribution=None):
    """Sample an agent type from a distribution.
    
    Args:
        types: list of type names
        distribution: list of probabilities (must sum to 1), or None for uniform
    
    Returns:
        type name (string)
    """
    if distribution is None:
        distribution = [1.0/len(types)] * len(types)
    return np.random.choice(types, p=distribution)

# safer matching
def greedy_match(waiting, t, compatibility_matrix=None):
    matched_pairs = []
    unmatched = []
    used = set()
    for i, a in enumerate(waiting):
        if i in used: continue
        found = False
        for j, b in enumerate(waiting):
            if j in used or i == j: continue
            if are_compatible(a, b, compatibility_matrix=compatibility_matrix):
                a.matched = b.matched = True
                a.match_time = b.match_time = t
                a.partner_id, b.partner_id = b.id, a.id
                used.add(i); used.add(j)
                matched_pairs.append((a,b,t))
                found = True
                break
        if not found: unmatched.append(a)
    return matched_pairs, [a for i,a in enumerate(waiting) if i not in used]

def patient_match(waiting, t, compatibility_matrix=None):
    """Patient matching: expiring agents match with full pool.
    
    Following Akbarpour-Li-Oveis Gharan: when an agent becomes critical,
    match them with anyone compatible in the full waiting pool, not just
    other expiring agents.
    """
    expiring = [a for a in waiting if a.deadline <= t]
    stay = [a for a in waiting if a.deadline > t]
    
    if not expiring:
        return [], waiting
    
    pairs = []
    used_ids = set()
    pool = stay + expiring
    
    # For each expiring agent, try to match with anyone in the full pool
    for a in expiring:
        if a.id in used_ids:
            continue
        for b in pool:
            if b.id in used_ids or b.id == a.id:
                continue
            if are_compatible(a, b, compatibility_matrix=compatibility_matrix):
                # Mark both matched
                a.matched = b.matched = True
                a.match_time = b.match_time = t
                a.partner_id, b.partner_id = b.id, a.id
                used_ids.add(a.id)
                used_ids.add(b.id)
                pairs.append((a, b, t))
                break
    
    # Return unmatched agents who haven't expired
    remaining = [x for x in pool if x.id not in used_ids and not x.is_expired(t)]
    return pairs, remaining

def patient_alpha_match(waiting, t, alpha=0.3, compatibility_matrix=None):
    if random.random() < alpha:
        return greedy_match(waiting, t, compatibility_matrix)
    else:
        return patient_match(waiting, t, compatibility_matrix)

def urgency_aware_match(waiting, t, compatibility_matrix=None, urgency_threshold=None):
    """Prioritize matching high-urgency agents.
    
    Sort agents by time until deadline, then try to match most urgent first.
    """
    if not waiting:
        return [], []
    
    # Sort by urgency (time remaining until deadline)
    sorted_waiting = sorted(waiting, key=lambda a: a.time_until_deadline(t))
    
    # If threshold provided, only match agents above urgency threshold
    if urgency_threshold is not None:
        urgent = [a for a in sorted_waiting if a.time_until_deadline(t) <= urgency_threshold]
        non_urgent = [a for a in sorted_waiting if a.time_until_deadline(t) > urgency_threshold]
        pairs, remaining_urgent = greedy_match(urgent, t, compatibility_matrix)
        return pairs, remaining_urgent + non_urgent
    else:
        # Match all, but in urgency order
        return greedy_match(sorted_waiting, t, compatibility_matrix)

def adaptive_alpha_match(waiting, t, compatibility_matrix=None, base_alpha=0.3):
    """Adjust greediness based on average urgency in the pool.
    
    When pool is generally urgent (short deadlines), be more greedy.
    When pool has time, be more patient.
    """
    if not waiting:
        return [], []
    
    # Calculate average time until deadline
    avg_time_remaining = np.mean([a.time_until_deadline(t) for a in waiting])
    
    # Adjust alpha: more urgent pool -> higher alpha (more greedy)
    # Use sigmoid-like function to map time remaining to alpha
    if avg_time_remaining < 5:
        adjusted_alpha = min(1.0, base_alpha * 2.0)  # very urgent -> very greedy
    elif avg_time_remaining < 10:
        adjusted_alpha = base_alpha * 1.5
    elif avg_time_remaining > 20:
        adjusted_alpha = max(0.0, base_alpha * 0.5)  # lots of time -> be patient
    else:
        adjusted_alpha = base_alpha
    
    return patient_alpha_match(waiting, t, adjusted_alpha, compatibility_matrix)

def poisson_arrivals(rate, T):
    t, arrivals = 0, []
    while t < T:
        t += random.expovariate(rate)
        if t <= T: arrivals.append(t)
    return arrivals

def run_simulation(T=100, arrival_rate=1.0, easy_fraction=0.7,
                   avg_deadline=10.0, policy=Policy.GREEDY,
                   alpha=0.3, waiting_cost_per_unit=0.05, seed=None,
                   compatibility_matrix=None, agent_types=None, type_distribution=None):
    """Run dynamic matching simulation.
    
    Args:
        T: simulation horizon
        arrival_rate: Poisson arrival rate
        easy_fraction: fraction of "easy" agents (only used if agent_types=None)
        avg_deadline: average agent deadline
        policy: matching policy
        alpha: greediness parameter for PATIENT_ALPHA
        waiting_cost_per_unit: waiting cost coefficient
        seed: random seed
        compatibility_matrix: custom compatibility matrix dict
        agent_types: list of type names (if None, uses ["easy", "hard"])
        type_distribution: probability distribution over types
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    # Set up agent types
    if agent_types is None:
        agent_types = ["easy", "hard"]
        if type_distribution is None:
            type_distribution = [easy_fraction, 1 - easy_fraction]
    
    arrivals = poisson_arrivals(arrival_rate, T)
    arrivals.sort()
    waiting, all_agents, matches = [], [], []
    idx, current_time = 0, 0
    while (current_time <= T or idx < len(arrivals)):
        if idx < len(arrivals): current_time = arrivals[idx]
        else: current_time += 1
        # add new agents
        while idx < len(arrivals) and abs(arrivals[idx]-current_time) < 1e-9:
            agent_type = sample_agent_type(agent_types, type_distribution)
            deadline = current_time + random.expovariate(1.0/avg_deadline)
            cost = waiting_cost_per_unit*random.uniform(0.5,1.5)
            a = Agent(current_time, deadline, agent_type, cost)
            waiting.append(a); all_agents.append(a); idx += 1
        # FIXED: match BEFORE removing expired agents
        if policy == Policy.GREEDY:
            pairs, waiting = greedy_match(waiting, current_time, compatibility_matrix)
        elif policy == Policy.PATIENT:
            pairs, waiting = patient_match(waiting, current_time, compatibility_matrix)
        elif policy == Policy.PATIENT_ALPHA:
            pairs, waiting = patient_alpha_match(waiting, current_time, alpha, compatibility_matrix)
        elif policy == Policy.URGENCY_AWARE:
            pairs, waiting = urgency_aware_match(waiting, current_time, compatibility_matrix)
        elif policy == Policy.ADAPTIVE_ALPHA:
            pairs, waiting = adaptive_alpha_match(waiting, current_time, compatibility_matrix, alpha)
        else:
            pairs, waiting = greedy_match(waiting, current_time, compatibility_matrix)
        matches.extend(pairs)
        # NOW remove expired agents (who failed to match)
        waiting = [a for a in waiting if not a.is_expired(current_time)]
        # safety break
        if current_time > T*2: break
    # compute overall metrics
    matched = [a for a in all_agents if a.matched]
    unmatched = [a for a in all_agents if not a.matched]
    welfare = sum(1 - a.patience_cost*(a.match_time-a.arrival_time)
                  for a in matched)
    avg_wait = sum(a.match_time - a.arrival_time for a in matched)/len(matched) if matched else 0
    
    # compute metrics by type (for all types present in simulation)
    unique_types = set(a.agent_type for a in all_agents)
    metrics_by_type = {}
    for agent_type in unique_types:
        type_agents = [a for a in all_agents if a.agent_type == agent_type]
        if not type_agents:
            continue
        type_matched = [a for a in type_agents if a.matched]
        type_unmatched = [a for a in type_agents if not a.matched]
        type_welfare = sum(1 - a.patience_cost*(a.match_time-a.arrival_time)
                          for a in type_matched)
        type_avg_wait = sum(a.match_time - a.arrival_time for a in type_matched)/len(type_matched) if type_matched else 0
        metrics_by_type[agent_type] = {
            "match_rate": len(type_matched)/len(type_agents),
            "avg_wait": type_avg_wait,
            "welfare": type_welfare,
            "matched": len(type_matched),
            "unmatched": len(type_unmatched),
            "total": len(type_agents),
            "expired_unmatched_rate": len(type_unmatched)/len(type_agents)
        }
    
    return {
        "match_rate": len(matched)/len(all_agents),
        "avg_wait": avg_wait,
        "welfare": welfare,
        "matched": len(matched),
        "unmatched": len(unmatched),
        "total": len(all_agents),
        "by_type": metrics_by_type
    }

def run_simulation_averaged(n_seeds=10, **kwargs):
    """Run simulation multiple times and average results.
    
    Args:
        n_seeds: Number of random seeds to average over
        **kwargs: Parameters for run_simulation
    
    Returns:
        dict with averaged metrics and std deviations
    """
    results_list = []
    base_seed = kwargs.get('seed', 0)
    
    for i in range(n_seeds):
        kwargs['seed'] = base_seed + i if base_seed is not None else None
        results_list.append(run_simulation(**kwargs))
    
    # Average metrics
    averaged = {
        'match_rate': np.mean([r['match_rate'] for r in results_list]),
        'match_rate_std': np.std([r['match_rate'] for r in results_list]),
        'avg_wait': np.mean([r['avg_wait'] for r in results_list]),
        'avg_wait_std': np.std([r['avg_wait'] for r in results_list]),
        'welfare': np.mean([r['welfare'] for r in results_list]),
        'welfare_std': np.std([r['welfare'] for r in results_list]),
        'n_seeds': n_seeds
    }
    
    # Average by-type metrics if present
    if results_list[0]['by_type']:
        averaged['by_type'] = {}
        for agent_type in results_list[0]['by_type'].keys():
            averaged['by_type'][agent_type] = {
                'match_rate': np.mean([r['by_type'][agent_type]['match_rate'] 
                                      for r in results_list if agent_type in r['by_type']]),
                'avg_wait': np.mean([r['by_type'][agent_type]['avg_wait'] 
                                    for r in results_list if agent_type in r['by_type']]),
                'expired_unmatched_rate': np.mean([r['by_type'][agent_type]['expired_unmatched_rate'] 
                                                  for r in results_list if agent_type in r['by_type']])
            }
    
    return averaged

def run_baseline_comparisons(T=200, seed=0, verbose=True, include_urgency=False, n_seeds=1):
    """Compare all policies on homogeneous and imbalanced markets."""
    results = {}
    
    policies = [Policy.GREEDY, Policy.PATIENT, Policy.PATIENT_ALPHA]
    if include_urgency:
        policies.extend([Policy.URGENCY_AWARE, Policy.ADAPTIVE_ALPHA])
    
    if n_seeds > 1 and verbose:
        print(f"(Averaging over {n_seeds} runs)")
    
    if verbose:
        print("=== Homogeneous market (easy=0.9) ===")
    results['homogeneous'] = {}
    for policy in policies:
        if n_seeds > 1:
            res = run_simulation_averaged(n_seeds=n_seeds, T=T, easy_fraction=0.9, 
                                         policy=policy, seed=seed)
        else:
            res = run_simulation(T=T, easy_fraction=0.9, policy=policy, seed=seed)
        results['homogeneous'][policy.name] = res
        if verbose:
            print(f"{policy.name}:")
            if n_seeds > 1:
                print(f"  Match rate: {res['match_rate']:.3f} ± {res['match_rate_std']:.3f}")
                print(f"  Avg wait: {res['avg_wait']:.2f} ± {res['avg_wait_std']:.2f}")
                print(f"  Welfare: {res['welfare']:.1f} ± {res['welfare_std']:.1f}")
            else:
                print(f"  Match rate: {res['match_rate']:.3f}, Avg wait: {res['avg_wait']:.2f}, Welfare: {res['welfare']:.1f}")
                for agent_type, metrics in res['by_type'].items():
                    print(f"  {agent_type.capitalize()} - Match: {metrics['match_rate']:.3f}, "
                          f"Wait: {metrics['avg_wait']:.2f}, Expired: {metrics['expired_unmatched_rate']:.3f}")

    if verbose:
        print("\n=== Imbalanced market (easy=0.3) ===")
    results['imbalanced'] = {}
    for policy in policies:
        if n_seeds > 1:
            res = run_simulation_averaged(n_seeds=n_seeds, T=T, easy_fraction=0.3, 
                                         policy=policy, seed=seed)
        else:
            res = run_simulation(T=T, easy_fraction=0.3, policy=policy, seed=seed)
        results['imbalanced'][policy.name] = res
        if verbose:
            print(f"{policy.name}:")
            if n_seeds > 1:
                print(f"  Match rate: {res['match_rate']:.3f} ± {res['match_rate_std']:.3f}")
                print(f"  Avg wait: {res['avg_wait']:.2f} ± {res['avg_wait_std']:.2f}")
                print(f"  Welfare: {res['welfare']:.1f} ± {res['welfare_std']:.1f}")
            else:
                print(f"  Match rate: {res['match_rate']:.3f}, Avg wait: {res['avg_wait']:.2f}, Welfare: {res['welfare']:.1f}")
                for agent_type, metrics in res['by_type'].items():
                    print(f"  {agent_type.capitalize()} - Match: {metrics['match_rate']:.3f}, "
                          f"Wait: {metrics['avg_wait']:.2f}, Expired: {metrics['expired_unmatched_rate']:.3f}")
    
    return results

def run_heterogeneity_experiments(T=200, seed=0, verbose=True):
    """Test policies across varying levels of market heterogeneity."""
    easy_fractions = [0.1, 0.3, 0.5, 0.7, 0.9]
    results = defaultdict(lambda: defaultdict(list))
    
    for ef in easy_fractions:
        for policy in [Policy.GREEDY, Policy.PATIENT, Policy.PATIENT_ALPHA]:
            res = run_simulation(T=T, easy_fraction=ef, policy=policy, seed=seed)
            results[policy.name]['easy_fraction'].append(ef)
            results[policy.name]['match_rate'].append(res['match_rate'])
            results[policy.name]['avg_wait'].append(res['avg_wait'])
            results[policy.name]['welfare'].append(res['welfare'])
    
    if verbose:
        print("=== Heterogeneity Experiments ===")
        for policy_name, data in results.items():
            print(f"\n{policy_name}:")
            for i, ef in enumerate(easy_fractions):
                print(f"  easy_frac={ef:.1f}: match_rate={data['match_rate'][i]:.3f}, "
                      f"avg_wait={data['avg_wait'][i]:.2f}, welfare={data['welfare'][i]:.1f}")
    
    return dict(results)

def test_multitype_compatibility(n_types=4, structure='clustered', T=200, seed=0, include_urgency=False):
    """Test policies with multi-type compatibility structures."""
    compat_matrix, types = create_compatibility_matrix(n_types, structure=structure)
    
    print(f"\n=== Multi-Type Experiment: {n_types} types, {structure} structure ===")
    print(f"Types: {types}")
    
    policies = [Policy.GREEDY, Policy.PATIENT, Policy.PATIENT_ALPHA]
    if include_urgency:
        policies.extend([Policy.URGENCY_AWARE, Policy.ADAPTIVE_ALPHA])
    
    results = {}
    for policy in policies:
        res = run_simulation(T=T, policy=policy, seed=seed,
                           compatibility_matrix=compat_matrix,
                           agent_types=types,
                           type_distribution=None)  # uniform distribution
        results[policy.name] = res
        print(f"\n{policy.name}:")
        print(f"  Overall - Match rate: {res['match_rate']:.3f}, Avg wait: {res['avg_wait']:.2f}")
        for agent_type, metrics in sorted(res['by_type'].items()):
            print(f"  {agent_type} - Match rate: {metrics['match_rate']:.3f}, "
                  f"Avg wait: {metrics['avg_wait']:.2f}, Count: {metrics['total']}")
    
    return results

def test_urgency_policies(avg_deadline=10.0, T=200, seed=0):
    """Compare urgency-aware policies with baseline policies."""
    print(f"\n=== Urgency Policy Comparison (avg_deadline={avg_deadline}) ===")
    
    policies = [Policy.GREEDY, Policy.PATIENT, Policy.URGENCY_AWARE, Policy.ADAPTIVE_ALPHA]
    results = {}
    
    for policy in policies:
        res = run_simulation(T=T, avg_deadline=avg_deadline, policy=policy, seed=seed)
        results[policy.name] = res
        print(f"\n{policy.name}:")
        print(f"  Match rate: {res['match_rate']:.3f}")
        print(f"  Avg wait: {res['avg_wait']:.2f}")
        print(f"  Welfare: {res['welfare']:.1f}")
    
    return results

if __name__ == "__main__":
    # Run baseline comparisons with the original 2-type system
    run_baseline_comparisons(T=200, seed=0)
    
    # Uncomment to test multi-type systems:
    # test_multitype_compatibility(n_types=4, structure='clustered', T=200, seed=0)
    # test_multitype_compatibility(n_types=5, structure='core_periphery', T=200, seed=0)
        
def plot_alpha_sweep(easy_fraction, T=200, seed=0, save_fig=False):
    """Sweep alpha parameter for PATIENT_ALPHA policy."""
    alphas = [i / 10 for i in range(0, 11)]
    match_rates, welfares = [], []

    for a in alphas:
        res = run_simulation(T=T, easy_fraction=easy_fraction,
                             policy=Policy.PATIENT_ALPHA, alpha=a, seed=seed)
        match_rates.append(res["match_rate"])
        welfares.append(res["welfare"])

    plt.figure(figsize=(10,4))
    plt.subplot(1,2,1)
    plt.plot(alphas, match_rates, marker='o')
    plt.title(f"Match Rate vs Alpha (easy_fraction={easy_fraction})")
    plt.xlabel("Alpha (Greediness)")
    plt.ylabel("Match Rate")
    plt.grid(True, alpha=0.3)

    plt.subplot(1,2,2)
    plt.plot(alphas, welfares, marker='o', color='orange')
    plt.title(f"Welfare vs Alpha (easy_fraction={easy_fraction})")
    plt.xlabel("Alpha (Greediness)")
    plt.ylabel("Welfare")
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    if save_fig:
        plt.savefig(f'alpha_sweep_ef{easy_fraction}.png', dpi=150)
    plt.show()

def sweep_parameters(param_name='arrival_rate', param_values=None, 
                     T=200, policy=Policy.GREEDY, seed=0, **fixed_params):
    """Sweep a single parameter and return results.
    
    Args:
        param_name: one of 'arrival_rate', 'avg_deadline', 'easy_fraction', 'alpha'
        param_values: list of values to sweep
        T: simulation horizon
        policy: Policy enum
        seed: random seed
        **fixed_params: other parameters to keep fixed
    """
    if param_values is None:
        if param_name == 'arrival_rate':
            param_values = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
        elif param_name == 'avg_deadline':
            param_values = [5, 10, 15, 20, 30]
        elif param_name == 'easy_fraction':
            param_values = [0.1, 0.3, 0.5, 0.7, 0.9]
        elif param_name == 'alpha':
            param_values = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    
    results = {'param_values': param_values, 'match_rate': [], 
               'avg_wait': [], 'welfare': []}
    
    for val in param_values:
        params = fixed_params.copy()
        params[param_name] = val
        res = run_simulation(T=T, policy=policy, seed=seed, **params)
        results['match_rate'].append(res['match_rate'])
        results['avg_wait'].append(res['avg_wait'])
        results['welfare'].append(res['welfare'])
    
    return results

def plot_parameter_sweep(param_name, policies=None, T=200, seed=0, 
                         param_values=None, save_fig=False, **fixed_params):
    """Plot parameter sweep for multiple policies."""
    if policies is None:
        policies = [Policy.GREEDY, Policy.PATIENT, Policy.PATIENT_ALPHA]
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    for policy in policies:
        results = sweep_parameters(param_name, param_values, T, policy, seed, **fixed_params)
        
        axes[0].plot(results['param_values'], results['match_rate'], 
                     marker='o', label=policy.name)
        axes[1].plot(results['param_values'], results['avg_wait'], 
                     marker='s', label=policy.name)
        axes[2].plot(results['param_values'], results['welfare'], 
                     marker='^', label=policy.name)
    
    axes[0].set_xlabel(param_name.replace('_', ' ').title())
    axes[0].set_ylabel('Match Rate')
    axes[0].set_title('Match Rate')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    axes[1].set_xlabel(param_name.replace('_', ' ').title())
    axes[1].set_ylabel('Avg Wait Time')
    axes[1].set_title('Average Wait Time')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    axes[2].set_xlabel(param_name.replace('_', ' ').title())
    axes[2].set_ylabel('Welfare')
    axes[2].set_title('Total Welfare')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    if save_fig:
        plt.savefig(f'{param_name}_sweep.png', dpi=150)
    plt.show()

def generate_heatmap(param1_name='arrival_rate', param2_name='avg_deadline',
                     policy=Policy.GREEDY, metric='match_rate', T=200, seed=0,
                     param1_values=None, param2_values=None, save_fig=False, **fixed_params):
    """Generate heatmap showing how a metric varies across two parameters."""
    if param1_values is None:
        param1_values = [0.5, 1.0, 1.5, 2.0, 2.5] if param1_name == 'arrival_rate' else [0.2, 0.4, 0.6, 0.8]
    if param2_values is None:
        param2_values = [5, 10, 15, 20, 30] if param2_name == 'avg_deadline' else [0.2, 0.4, 0.6, 0.8]
    
    results = np.zeros((len(param2_values), len(param1_values)))
    
    for i, p2 in enumerate(param2_values):
        for j, p1 in enumerate(param1_values):
            params = fixed_params.copy()
            params[param1_name] = p1
            params[param2_name] = p2
            res = run_simulation(T=T, policy=policy, seed=seed, **params)
            results[i, j] = res[metric]
    
    plt.figure(figsize=(10, 8))
    im = plt.imshow(results, aspect='auto', cmap='viridis', origin='lower')
    plt.colorbar(im, label=metric.replace('_', ' ').title())
    
    plt.xticks(range(len(param1_values)), [f'{v:.1f}' for v in param1_values])
    plt.yticks(range(len(param2_values)), [f'{v:.1f}' for v in param2_values])
    
    plt.xlabel(param1_name.replace('_', ' ').title())
    plt.ylabel(param2_name.replace('_', ' ').title())
    plt.title(f'{metric.replace("_", " ").title()} - {policy.name} Policy')
    
    # Add text annotations
    for i in range(len(param2_values)):
        for j in range(len(param1_values)):
            text = plt.text(j, i, f'{results[i, j]:.2f}',
                          ha="center", va="center", color="w", fontsize=8)
    
    plt.tight_layout()
    if save_fig:
        plt.savefig(f'heatmap_{param1_name}_{param2_name}_{policy.name}.png', dpi=150)
    plt.show()


