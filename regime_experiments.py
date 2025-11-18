"""
Regime Comparison Experiments

Demonstrates how parameter choices affect relative performance of matching policies.
Shows both greedy-favorable and patient-favorable regimes per theoretical predictions.
"""

from sim import *

def test_greedy_favorable_regime(T=200, seed=42, n_seeds=1):
    """
    Greedy-favorable regime: short deadlines, high compatibility.
    
    Theory predicts: GREEDY ≈ optimal, PATIENT struggles
    """
    print("=" * 70)
    print("GREEDY-FAVORABLE REGIME")
    print("=" * 70)
    print("Short deadlines (10), high compatibility (0.9, 0.4, 0.1)")
    print("Theory: Greedy should dominate")
    print()
    
    policies = [Policy.GREEDY, Policy.PATIENT, Policy.PATIENT_ALPHA]
    results = {}
    
    for policy in policies:
        if n_seeds > 1:
            res = run_simulation_averaged(
                n_seeds=n_seeds,
                T=T,
                arrival_rate=1.0,
                avg_deadline=10.0,
                easy_fraction=0.7,
                waiting_cost_per_unit=0.05,
                policy=policy,
                seed=seed
            )
            print(f"{policy.name}:")
            print(f"  Match rate: {res['match_rate']:.3f} ± {res['match_rate_std']:.3f}")
            print(f"  Avg wait: {res['avg_wait']:.2f} ± {res['avg_wait_std']:.2f}")
            print(f"  Welfare: {res['welfare']:.1f} ± {res['welfare_std']:.1f}")
        else:
            res = run_simulation(
                T=T,
                arrival_rate=1.0,
                avg_deadline=10.0,
                easy_fraction=0.7,
                waiting_cost_per_unit=0.05,
                policy=policy,
                seed=seed
            )
            print(f"{policy.name}:")
            print(f"  Match rate: {res['match_rate']:.3f}, Avg wait: {res['avg_wait']:.2f}, Welfare: {res['welfare']:.1f}")
            for agent_type, metrics in res['by_type'].items():
                print(f"  {agent_type.capitalize()} - Match: {metrics['match_rate']:.3f}, "
                      f"Expired: {metrics['expired_unmatched_rate']:.3f}")
        results[policy.name] = res
        print()
    
    return results

def test_patient_favorable_regime(T=200, seed=42, n_seeds=1):
    """
    Patient-favorable regime: long deadlines, sparse compatibility.
    
    Theory predicts: PATIENT can achieve higher match rates by thickening
    the market, despite longer waits.
    """
    print("=" * 70)
    print("PATIENT-FAVORABLE REGIME")
    print("=" * 70)
    print("Long deadlines (70), sparse compatibility (0.25, 0.08, 0.02)")
    print("Lower waiting costs (0.01)")
    print("Theory: PATIENT should increase match rates, especially for hard types")
    print()
    
    # Create sparse compatibility matrix
    types = ["easy", "hard"]
    sparse_matrix = {
        ("easy", "easy"): 0.25,
        ("easy", "hard"): 0.08,
        ("hard", "easy"): 0.08,
        ("hard", "hard"): 0.02
    }
    
    policies = [Policy.GREEDY, Policy.PATIENT, Policy.PATIENT_ALPHA]
    results = {}
    
    for policy in policies:
        if n_seeds > 1:
            res = run_simulation_averaged(
                n_seeds=n_seeds,
                T=T,
                arrival_rate=1.0,
                avg_deadline=70.0,
                waiting_cost_per_unit=0.01,
                policy=policy,
                seed=seed,
                compatibility_matrix=sparse_matrix,
                agent_types=types,
                type_distribution=[0.7, 0.3]
            )
            print(f"{policy.name}:")
            print(f"  Match rate: {res['match_rate']:.3f} ± {res['match_rate_std']:.3f}")
            print(f"  Avg wait: {res['avg_wait']:.2f} ± {res['avg_wait_std']:.2f}")
            print(f"  Welfare: {res['welfare']:.1f} ± {res['welfare_std']:.1f}")
        else:
            res = run_simulation(
                T=T,
                arrival_rate=1.0,
                avg_deadline=70.0,
                waiting_cost_per_unit=0.01,
                policy=policy,
                seed=seed,
                compatibility_matrix=sparse_matrix,
                agent_types=types,
                type_distribution=[0.7, 0.3]
            )
            print(f"{policy.name}:")
            print(f"  Match rate: {res['match_rate']:.3f}, Avg wait: {res['avg_wait']:.2f}, Welfare: {res['welfare']:.1f}")
            for agent_type, metrics in res['by_type'].items():
                print(f"  {agent_type.capitalize()} - Match: {metrics['match_rate']:.3f}, "
                      f"Wait: {metrics['avg_wait']:.2f}, Expired: {metrics['expired_unmatched_rate']:.3f}")
        results[policy.name] = res
        print()
    
    return results

def test_sparse_compatibility_regime(T=200, seed=42, n_seeds=1):
    """
    Test with explicitly sparse compatibility matrix.
    
    Creates a regime where edges are rare, so thickness really matters.
    """
    print("=" * 70)
    print("SPARSE COMPATIBILITY REGIME")
    print("=" * 70)
    print("Long deadlines (50), very sparse compatibility")
    print("easy-easy: 0.25, easy-hard: 0.08, hard-hard: 0.02")
    print()
    
    # Override are_compatible by modifying defaults - we need to modify the sim
    # For now, let's use a compatibility matrix
    types = ["easy", "hard"]
    sparse_matrix = {
        ("easy", "easy"): 0.25,
        ("easy", "hard"): 0.08,
        ("hard", "easy"): 0.08,
        ("hard", "hard"): 0.02
    }
    
    policies = [Policy.GREEDY, Policy.PATIENT, Policy.PATIENT_ALPHA]
    results = {}
    
    for policy in policies:
        if n_seeds > 1:
            res = run_simulation_averaged(
                n_seeds=n_seeds,
                T=T,
                arrival_rate=1.0,
                avg_deadline=50.0,
                waiting_cost_per_unit=0.01,
                policy=policy,
                seed=seed,
                compatibility_matrix=sparse_matrix,
                agent_types=types,
                type_distribution=[0.7, 0.3]
            )
            print(f"{policy.name}:")
            print(f"  Match rate: {res['match_rate']:.3f} ± {res['match_rate_std']:.3f}")
            print(f"  Avg wait: {res['avg_wait']:.2f} ± {res['avg_wait_std']:.2f}")
        else:
            res = run_simulation(
                T=T,
                arrival_rate=1.0,
                avg_deadline=50.0,
                waiting_cost_per_unit=0.01,
                policy=policy,
                seed=seed,
                compatibility_matrix=sparse_matrix,
                agent_types=types,
                type_distribution=[0.7, 0.3]
            )
            print(f"{policy.name}:")
            print(f"  Match rate: {res['match_rate']:.3f}, Avg wait: {res['avg_wait']:.2f}")
            for agent_type, metrics in res['by_type'].items():
                print(f"  {agent_type.capitalize()} - Match: {metrics['match_rate']:.3f}, "
                      f"Wait: {metrics['avg_wait']:.2f}, Expired: {metrics['expired_unmatched_rate']:.3f}")
        results[policy.name] = res
        print()
    
    return results

def test_alpha_tradeoff(T=200, seed=42, regime='patient_favorable'):
    """
    Show the match rate vs welfare tradeoff as alpha varies.
    """
    print("=" * 70)
    print(f"ALPHA SWEEP: {regime.upper()} REGIME")
    print("=" * 70)
    print("Showing speed-thickness tradeoff for PATIENT_ALPHA")
    print()
    
    if regime == 'patient_favorable':
        params = {
            'avg_deadline': 70.0,
            'waiting_cost_per_unit': 0.01
        }
    else:
        params = {
            'avg_deadline': 10.0,
            'waiting_cost_per_unit': 0.05
        }
    
    alphas = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    match_rates = []
    welfares = []
    avg_waits = []
    
    for alpha in alphas:
        res = run_simulation(
            T=T,
            arrival_rate=1.0,
            easy_fraction=0.7,
            policy=Policy.PATIENT_ALPHA,
            alpha=alpha,
            seed=seed,
            **params
        )
        match_rates.append(res['match_rate'])
        welfares.append(res['welfare'])
        avg_waits.append(res['avg_wait'])
    
    print(f"{'Alpha':<10} {'Match Rate':<12} {'Avg Wait':<12} {'Welfare':<12}")
    print("-" * 50)
    for i, alpha in enumerate(alphas):
        print(f"{alpha:<10.1f} {match_rates[i]:<12.3f} {avg_waits[i]:<12.2f} {welfares[i]:<12.1f}")
    
    # Plotting
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    axes[0].plot(alphas, match_rates, 'o-', linewidth=2)
    axes[0].set_xlabel('Alpha (Greediness)')
    axes[0].set_ylabel('Match Rate')
    axes[0].set_title('Match Rate vs Alpha')
    axes[0].grid(True, alpha=0.3)
    
    axes[1].plot(alphas, avg_waits, 'o-', linewidth=2, color='orange')
    axes[1].set_xlabel('Alpha (Greediness)')
    axes[1].set_ylabel('Avg Wait Time')
    axes[1].set_title('Wait Time vs Alpha')
    axes[1].grid(True, alpha=0.3)
    
    axes[2].plot(alphas, welfares, 'o-', linewidth=2, color='green')
    axes[2].set_xlabel('Alpha (Greediness)')
    axes[2].set_ylabel('Welfare')
    axes[2].set_title('Welfare vs Alpha')
    axes[2].grid(True, alpha=0.3)
    
    plt.suptitle(f'PATIENT_ALPHA Trade-offs: {regime.replace("_", " ").title()} Regime')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    print("REGIME COMPARISON EXPERIMENTS")
    print("Demonstrating how parameter choices affect policy performance")
    print()
    
    # 1. Greedy-favorable regime (current default)
    test_greedy_favorable_regime(T=200, seed=42, n_seeds=10)
    
    # 2. Patient-favorable regime
    test_patient_favorable_regime(T=200, seed=42, n_seeds=10)
    
    # 3. Sparse compatibility
    test_sparse_compatibility_regime(T=200, seed=42, n_seeds=10)
    
    # 4. Alpha trade-offs
    # test_alpha_tradeoff(T=200, seed=42, regime='patient_favorable')
    # test_alpha_tradeoff(T=200, seed=42, regime='greedy_favorable')
