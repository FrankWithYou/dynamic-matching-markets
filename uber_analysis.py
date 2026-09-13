"""
Comprehensive Analysis and Visualization for Uber-Like Simulator

Creates detailed visualizations and statistical analysis of uber_sim results.
"""

from uber_sim import *
import matplotlib.pyplot as plt
import numpy as np

def analyze_policy_comparison(T=240, seed=42, save_fig=False):
    """Comprehensive analysis of spatial matching policies.
    
    Uses busy market parameters:
    - T=240 (4 hours simulated)
    - rider_arrival_rate=4.0 (high demand)
    - driver_arrival_rate=0.5 (8:1 rider:driver ratio)
    - avg_trip_distance=6.0 (longer trips)
    - Target utilization: ~40-60%
    """
    print("=" * 70)
    print("UBER POLICY ANALYSIS WITH VISUALIZATIONS")
    print("=" * 70)
    print()
    
    policies = [MatchingPolicy.GREEDY, MatchingPolicy.FCFS, MatchingPolicy.DISTANCE_AWARE]
    results = {}
    
    print("Running simulations (busy market regime)...")
    for policy in policies:
        results[policy.name] = run_uber_simulation(
            T=T,
            rider_arrival_rate=4.0,      # much more demand
            driver_arrival_rate=0.5,     # fewer drivers
            avg_deadline=20.0,           # riders can wait a bit
            avg_trip_distance=6.0,       # longer trips
            location_model=LocationModel.GRID_2D,
            policy=policy,
            seed=seed
        )
    
    # Create comprehensive visualization
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.3)
    
    policy_names = list(results.keys())
    colors = ['#27ae60', '#e67e22', '#3498db']
    
    # 1. Match Rates
    ax1 = fig.add_subplot(gs[0, 0])
    match_rates = [results[p]['rider_match_rate'] for p in policy_names]
    bars1 = ax1.bar(policy_names, match_rates, color=colors, alpha=0.8, edgecolor='black')
    ax1.set_ylabel('Match Rate', fontweight='bold')
    ax1.set_title('Match Rate by Policy', fontweight='bold')
    ax1.set_ylim([0.6, 1.0])  # Wide enough for busy market regime
    ax1.grid(axis='y', alpha=0.3)
    for bar, val in zip(bars1, match_rates):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.1%}', ha='center', va='bottom', fontweight='bold')
    
    # 2. Wait Times (matched agents only)
    ax2 = fig.add_subplot(gs[0, 1])
    wait_times = [results[p]['avg_rider_wait'] for p in policy_names]
    bars2 = ax2.bar(policy_names, wait_times, color=colors, alpha=0.8, edgecolor='black')
    ax2.set_ylabel('Avg Wait (matched)', fontweight='bold')
    ax2.set_title('Wait Time for Matched Riders', fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    for bar, val in zip(bars2, wait_times):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.2f}', ha='center', va='bottom', fontweight='bold')
    
    # 3. Welfare
    ax3 = fig.add_subplot(gs[0, 2])
    welfares = [results[p]['welfare'] for p in policy_names]
    bars3 = ax3.bar(policy_names, welfares, color=colors, alpha=0.8, edgecolor='black')
    ax3.set_ylabel('Welfare', fontweight='bold')
    ax3.set_title('Total Welfare', fontweight='bold')
    ax3.grid(axis='y', alpha=0.3)
    for bar, val in zip(bars3, welfares):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.1f}', ha='center', va='bottom', fontweight='bold')
    
    # 4. Pickup Distance
    ax4 = fig.add_subplot(gs[1, 0])
    pickup_dists = [results[p]['avg_pickup_distance'] for p in policy_names]
    bars4 = ax4.bar(policy_names, pickup_dists, color=colors, alpha=0.8, edgecolor='black')
    ax4.set_ylabel('Avg Pickup Distance', fontweight='bold')
    ax4.set_title('Driver Pickup Distance', fontweight='bold')
    ax4.grid(axis='y', alpha=0.3)
    for bar, val in zip(bars4, pickup_dists):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.2f}', ha='center', va='bottom', fontweight='bold')
    
    # 5. Driver Utilization
    ax5 = fig.add_subplot(gs[1, 1])
    utils = [results[p]['driver_utilization'] * 100 for p in policy_names]
    bars5 = ax5.bar(policy_names, utils, color=colors, alpha=0.8, edgecolor='black')
    ax5.set_ylabel('Driver Utilization (%)', fontweight='bold')
    ax5.set_title('Driver Utilization', fontweight='bold')
    ax5.grid(axis='y', alpha=0.3)
    for bar, val in zip(bars5, utils):
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # 6. Trips per Driver
    ax6 = fig.add_subplot(gs[1, 2])
    trips = [results[p]['avg_trips_per_driver'] for p in policy_names]
    bars6 = ax6.bar(policy_names, trips, color=colors, alpha=0.8, edgecolor='black')
    ax6.set_ylabel('Avg Trips per Driver', fontweight='bold')
    ax6.set_title('Driver Productivity', fontweight='bold')
    ax6.grid(axis='y', alpha=0.3)
    for bar, val in zip(bars6, trips):
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.2f}', ha='center', va='bottom', fontweight='bold')
    
    # 7. Match Rate vs Wait Time (Speed-Thickness Tradeoff)
    ax7 = fig.add_subplot(gs[2, 0])
    for i, policy in enumerate(policy_names):
        ax7.scatter(wait_times[i], match_rates[i], s=300, 
                   color=colors[i], alpha=0.7, edgecolors='black', linewidth=2)
        ax7.annotate(policy, (wait_times[i], match_rates[i]),
                    xytext=(10, -10), textcoords='offset points',
                    fontweight='bold', fontsize=9)
    ax7.set_xlabel('Avg Wait Time (matched)', fontweight='bold')
    ax7.set_ylabel('Match Rate', fontweight='bold')
    ax7.set_title('Speed vs Match Rate', fontweight='bold')
    ax7.grid(True, alpha=0.3)
    
    # 8. Match Rate vs Welfare
    ax8 = fig.add_subplot(gs[2, 1])
    for i, policy in enumerate(policy_names):
        ax8.scatter(match_rates[i], welfares[i], s=300,
                   color=colors[i], alpha=0.7, edgecolors='black', linewidth=2)
        ax8.annotate(policy, (match_rates[i], welfares[i]),
                    xytext=(10, -10), textcoords='offset points',
                    fontweight='bold', fontsize=9)
    ax8.set_xlabel('Match Rate', fontweight='bold')
    ax8.set_ylabel('Welfare', fontweight='bold')
    ax8.set_title('Match Rate vs Welfare', fontweight='bold')
    ax8.grid(True, alpha=0.3)
    
    # 9. Summary Table
    ax9 = fig.add_subplot(gs[2, 2])
    ax9.axis('tight')
    ax9.axis('off')
    
    table_data = []
    metrics = ['Match Rate', 'Avg Wait', 'Welfare', 'Pickup Dist']
    for metric in metrics:
        row = [metric]
        if metric == 'Match Rate':
            row.extend([f"{results[p]['rider_match_rate']:.1%}" for p in policy_names])
        elif metric == 'Avg Wait':
            row.extend([f"{results[p]['avg_rider_wait']:.2f}" for p in policy_names])
        elif metric == 'Welfare':
            row.extend([f"{results[p]['welfare']:.1f}" for p in policy_names])
        else:  # Pickup Dist
            row.extend([f"{results[p]['avg_pickup_distance']:.2f}" for p in policy_names])
        table_data.append(row)
    
    n_cols = 1 + len(policy_names)  # 1 for 'Metric' + number of policies
    table = ax9.table(cellText=table_data, colLabels=['Metric'] + policy_names,
                     cellLoc='center', loc='center',
                     colColours=['lightgray'] * n_cols,
                     bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    ax9.set_title('Performance Summary', fontweight='bold', pad=20)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.suptitle('Uber-Like Market: Spatial Matching Policy Analysis (2D Grid)',
                fontsize=16, fontweight='bold', y=0.995)
    
    if save_fig:
        plt.savefig('uber_policy_analysis.png', dpi=300, bbox_inches='tight')
        print("Saved figure to 'uber_policy_analysis.png'")
    
    plt.show()
    
    # Print detailed analysis
    print("\n" + "=" * 70)
    print("DETAILED ANALYSIS")
    print("=" * 70)
    print(f"\nLocation Model: GRID_2D (Manhattan distance, realistic urban setting)")
    
    print("\n1. Policy Characteristics:")
    print("-" * 70)
    for policy in policy_names:
        r = results[policy]
        print(f"\n{policy}:")
        print(f"  Match Rate: {r['rider_match_rate']:.1%}")
        print(f"  Avg Wait: {r['avg_rider_wait']:.2f} time units")
        print(f"  Pickup Distance: {r['avg_pickup_distance']:.2f} units")
        print(f"  Driver Utilization: {r['driver_utilization']:.1%}")
        print(f"  Trips/Driver: {r['avg_trips_per_driver']:.2f}")
    
    print("\n2. Comparative Insights:")
    print("-" * 70)
    best_welfare_policy = max(policy_names, key=lambda p: results[p]['welfare'])
    print(f"  Best welfare: {best_welfare_policy} ({results[best_welfare_policy]['welfare']:.1f})")
    
    greedy_pickup = results['GREEDY']['avg_pickup_distance']
    fcfs_pickup = results['FCFS']['avg_pickup_distance']
    if greedy_pickup > 0:
        ratio = fcfs_pickup / greedy_pickup
        print(f"  FCFS pickup distance is {ratio:.1f}x GREEDY's")
        if ratio > 1.0:
            print("  → GREEDY's distance minimization reduces driver travel")
        else:
            print("  → In this busy regime, serving oldest riders first sometimes shortens pickups")
    
    print(f"\n  Key Tradeoff:")
    for policy in policy_names:
        mr = results[policy]['rider_match_rate']
        wt = results[policy]['avg_rider_wait']
        wf = results[policy]['welfare']
        print(f"    {policy}: {mr:.1%} matched, {wt:.2f} wait → {wf:.1f} welfare")
    
    return results

def analyze_supply_demand(T=240, seed=42, save_fig=False):
    """Analyze how supply-demand ratio affects market performance.
    
    Uses busy market parameters with varying supply ratios.
    Base: rider_arrival_rate=4.0, driver_arrival_rate scales around 0.5
    """
    print("\n" + "=" * 70)
    print("SUPPLY-DEMAND ANALYSIS")
    print("=" * 70)
    print()
    
    ratios = [0.5, 0.7, 0.9, 1.1, 1.3]  # scale around base driver rate
    results = []
    
    print("Running supply-demand experiments (busy market)...")
    for ratio in ratios:
        res = run_uber_simulation(
            T=T,
            rider_arrival_rate=4.0,           # keep fixed
            driver_arrival_rate=ratio * 0.5,  # scale around 0.5
            avg_deadline=20.0,
            avg_trip_distance=6.0,
            location_model=LocationModel.LINE_1D,
            policy=MatchingPolicy.GREEDY,
            seed=seed
        )
        results.append(res)
        print(f"  Ratio {ratio:.1f}: Match rate {res['rider_match_rate']:.1%}, "
              f"Utilization {res['driver_utilization']:.1%}")
    
    # Create visualization
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Match Rate
    axes[0, 0].plot(ratios, [r['rider_match_rate'] for r in results], 
                    'o-', linewidth=3, markersize=10, color='#27ae60')
    axes[0, 0].set_xlabel('Supply/Demand Ratio', fontweight='bold')
    axes[0, 0].set_ylabel('Rider Match Rate', fontweight='bold')
    axes[0, 0].set_title('Match Rate vs Supply', fontweight='bold', fontsize=12)
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].axvline(x=1.0, color='red', linestyle='--', alpha=0.3, label='Equal Supply')
    axes[0, 0].legend()
    
    # Wait Time
    axes[0, 1].plot(ratios, [r['avg_rider_wait'] for r in results], 
                    'o-', linewidth=3, markersize=10, color='#e67e22')
    axes[0, 1].set_xlabel('Supply/Demand Ratio', fontweight='bold')
    axes[0, 1].set_ylabel('Avg Rider Wait', fontweight='bold')
    axes[0, 1].set_title('Wait Time vs Supply', fontweight='bold', fontsize=12)
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].axvline(x=1.0, color='red', linestyle='--', alpha=0.3)
    
    # Driver Utilization
    axes[1, 0].plot(ratios, [r['driver_utilization'] * 100 for r in results], 
                    'o-', linewidth=3, markersize=10, color='#3498db')
    axes[1, 0].set_xlabel('Supply/Demand Ratio', fontweight='bold')
    axes[1, 0].set_ylabel('Driver Utilization (%)', fontweight='bold')
    axes[1, 0].set_title('Utilization vs Supply', fontweight='bold', fontsize=12)
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].axvline(x=1.0, color='red', linestyle='--', alpha=0.3)
    
    # Combined Efficiency
    axes[1, 1].plot(ratios, [r['rider_match_rate'] for r in results], 
                    'o-', linewidth=2, markersize=8, color='#27ae60')
    ax2 = axes[1, 1].twinx()
    ax2.plot(ratios, [r['driver_utilization'] * 100 for r in results],
            's-', linewidth=2, markersize=8, color='#3498db')
    
    axes[1, 1].set_xlabel('Supply/Demand Ratio', fontweight='bold')
    axes[1, 1].set_ylabel('Match Rate', fontweight='bold', color='#27ae60')
    ax2.set_ylabel('Driver Utilization (%)', fontweight='bold', color='#3498db')
    axes[1, 1].set_title('Match Rate vs Utilization Trade-off', fontweight='bold', fontsize=12)
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].axvline(x=1.0, color='red', linestyle='--', alpha=0.3)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.suptitle('Supply-Demand Analysis: Impact on Market Performance (1D Line)',
                fontsize=14, fontweight='bold', y=0.99)
    
    if save_fig:
        plt.savefig('uber_supply_demand.png', dpi=300, bbox_inches='tight')
        print("Saved figure to 'uber_supply_demand.png'")
    
    plt.show()
    
    # Analysis
    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)
    print(f"\nLocation Model: LINE_1D (simpler 1D space for clearer trends)")
    
    # Find optimal ratio
    best_match_idx = np.argmax([r['rider_match_rate'] for r in results])
    best_util_idx = np.argmax([r['driver_utilization'] for r in results])
    
    print(f"\nOptimal for match rate: ratio = {ratios[best_match_idx]:.1f}")
    print(f"  → {results[best_match_idx]['rider_match_rate']:.1%} of riders matched")
    
    print(f"\nOptimal for utilization: ratio = {ratios[best_util_idx]:.1f}")
    print(f"  → {results[best_util_idx]['driver_utilization']:.1%} driver utilization")
    
    print("\nTrade-off:")
    print("  Over-supply (ratio > 1.0):")
    print("    + Higher match rates")
    print("    - Lower driver utilization (wasted capacity)")
    print("  Under-supply (ratio < 1.0):")
    print("    + Higher driver utilization")
    print("    - Lower match rates, longer waits")
    
    return results

def analyze_location_models(T=240, seed=42, save_fig=False):
    """Compare different location models.
    
    Uses busy market parameters across different spatial structures.
    """
    print("\n" + "=" * 70)
    print("LOCATION MODEL COMPARISON")
    print("=" * 70)
    print()
    
    models = [
        (LocationModel.LINE_1D, "1D Line"),
        (LocationModel.GRID_2D, "2D Grid"),
        (LocationModel.TWO_REGION, "Two Regions")
    ]
    
    results = {}
    print("Running location model experiments (busy market)...")
    for model, name in models:
        res = run_uber_simulation(
            T=T,
            rider_arrival_rate=4.0,
            driver_arrival_rate=0.5,
            avg_deadline=20.0,
            avg_trip_distance=6.0,
            location_model=model,
            policy=MatchingPolicy.GREEDY,
            seed=seed
        )
        results[name] = res
        print(f"  {name}: Match {res['rider_match_rate']:.1%}, "
              f"Pickup dist {res['avg_pickup_distance']:.2f}, "
              f"Utilization {res['driver_utilization']:.1%}")
    
    # Visualization
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    names = list(results.keys())
    colors = ['#e74c3c', '#3498db', '#9b59b6']
    
    # Match rates
    match_rates = [results[n]['rider_match_rate'] for n in names]
    axes[0].bar(names, match_rates, color=colors, alpha=0.8, edgecolor='black')
    axes[0].set_ylabel('Match Rate', fontweight='bold')
    axes[0].set_title('Match Rate by Location Model', fontweight='bold')
    axes[0].set_ylim([0.6, 1.0])  # Wide enough for busy market regime
    axes[0].grid(axis='y', alpha=0.3)
    
    # Pickup distances
    pickup_dists = [results[n]['avg_pickup_distance'] for n in names]
    axes[1].bar(names, pickup_dists, color=colors, alpha=0.8, edgecolor='black')
    axes[1].set_ylabel('Avg Pickup Distance', fontweight='bold')
    axes[1].set_title('Pickup Distance by Location Model', fontweight='bold')
    axes[1].grid(axis='y', alpha=0.3)
    
    # Utilization
    utils = [results[n]['driver_utilization'] * 100 for n in names]
    axes[2].bar(names, utils, color=colors, alpha=0.8, edgecolor='black')
    axes[2].set_ylabel('Driver Utilization (%)', fontweight='bold')
    axes[2].set_title('Utilization by Location Model', fontweight='bold')
    axes[2].grid(axis='y', alpha=0.3)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.suptitle('Geographic Structure Impact on Market Performance',
                fontsize=14, fontweight='bold', y=0.99)
    
    if save_fig:
        plt.savefig('uber_location_models.png', dpi=300, bbox_inches='tight')
        print("Saved figure to 'uber_location_models.png'")
    
    plt.show()
    
    return results

if __name__ == "__main__":
    print("UBER MARKET COMPREHENSIVE ANALYSIS")
    print("Busy Market Regime: 4-hour horizon, 8:1 rider:driver ratio")
    print()
    
    # Run all analyses with visualizations (busy market parameters)
    analyze_policy_comparison(T=240, seed=42, save_fig=True)
    analyze_supply_demand(T=240, seed=42, save_fig=True)
    analyze_location_models(T=240, seed=42, save_fig=True)
    
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    print("\nGenerated visualizations:")
    print("  - uber_policy_analysis.png")
    print("  - uber_supply_demand.png")
    print("  - uber_location_models.png")
