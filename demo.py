"""
Demo script for Dynamic Matching Markets Simulator

This script demonstrates the various features and experiments available
in the simulator. Uncomment sections to run different experiments.
"""

from sim import *

def main():
    print("=" * 70)
    print("DYNAMIC MATCHING MARKETS SIMULATOR - DEMO")
    print("=" * 70)
    
    # ===================================================================
    # 1. BASELINE COMPARISONS
    # ===================================================================
    print("\n" + "=" * 70)
    print("1. BASELINE POLICY COMPARISONS")
    print("=" * 70)
    
    # Compare GREEDY, PATIENT, and PATIENT_ALPHA on standard markets
    results_basic = run_baseline_comparisons(T=200, seed=42, verbose=True)
    
    # Optionally include urgency-aware policies
    # print("\n--- Including Urgency-Aware Policies ---")
    # results_with_urgency = run_baseline_comparisons(
    #     T=200, seed=42, verbose=True, include_urgency=True
    # )
    
    # ===================================================================
    # 2. MARKET HETEROGENEITY EXPERIMENTS
    # ===================================================================
    print("\n" + "=" * 70)
    print("2. MARKET HETEROGENEITY EXPERIMENTS")
    print("=" * 70)
    
    # Test how policies perform across different market compositions
    heterogeneity_results = run_heterogeneity_experiments(
        T=200, seed=42, verbose=True
    )
    
    # ===================================================================
    # 3. ALPHA PARAMETER SWEEPS
    # ===================================================================
    print("\n" + "=" * 70)
    print("3. ALPHA PARAMETER SWEEPS")
    print("=" * 70)
    
    print("\nGenerating alpha sweep plots...")
    print("(Close plot windows to continue)")
    
    # Sweep alpha for homogeneous market
    plot_alpha_sweep(easy_fraction=0.9, T=200, seed=42)
    
    # Sweep alpha for imbalanced market
    plot_alpha_sweep(easy_fraction=0.3, T=200, seed=42)
    
    # ===================================================================
    # 4. PARAMETER SWEEPS
    # ===================================================================
    print("\n" + "=" * 70)
    print("4. SYSTEMATIC PARAMETER SWEEPS")
    print("=" * 70)
    
    print("\n4a. Arrival Rate Sweep (thin vs thick markets)")
    print("(Close plot window to continue)")
    
    plot_parameter_sweep(
        param_name='arrival_rate',
        param_values=[0.5, 1.0, 1.5, 2.0, 2.5],
        T=200,
        seed=42
    )
    
    print("\n4b. Deadline Sweep (patient vs impatient markets)")
    print("(Close plot window to continue)")
    
    plot_parameter_sweep(
        param_name='avg_deadline',
        param_values=[5, 10, 15, 20, 30],
        T=200,
        seed=42
    )
    
    print("\n4c. Market Composition Sweep")
    print("(Close plot window to continue)")
    
    plot_parameter_sweep(
        param_name='easy_fraction',
        param_values=[0.1, 0.3, 0.5, 0.7, 0.9],
        T=200,
        seed=42
    )
    
    # ===================================================================
    # 5. HEATMAP ANALYSIS
    # ===================================================================
    print("\n" + "=" * 70)
    print("5. HEATMAP ANALYSIS (2D Parameter Space)")
    print("=" * 70)
    
    print("\n5a. Match Rate: Arrival Rate vs Deadline")
    print("(Close plot window to continue)")
    
    generate_heatmap(
        param1_name='arrival_rate',
        param2_name='avg_deadline',
        param1_values=[0.5, 1.0, 1.5, 2.0],
        param2_values=[5, 10, 15, 20],
        policy=Policy.GREEDY,
        metric='match_rate',
        T=200,
        seed=42
    )
    
    print("\n5b. Welfare: Arrival Rate vs Easy Fraction")
    print("(Close plot window to continue)")
    
    generate_heatmap(
        param1_name='arrival_rate',
        param2_name='easy_fraction',
        param1_values=[0.5, 1.0, 1.5, 2.0],
        param2_values=[0.3, 0.5, 0.7, 0.9],
        policy=Policy.PATIENT_ALPHA,
        metric='welfare',
        T=200,
        seed=42,
        alpha=0.3
    )
    
    # ===================================================================
    # 6. MULTI-TYPE COMPATIBILITY EXPERIMENTS
    # ===================================================================
    print("\n" + "=" * 70)
    print("6. MULTI-TYPE COMPATIBILITY EXPERIMENTS")
    print("=" * 70)
    
    print("\n6a. Clustered Structure (4 types)")
    clustered_results = test_multitype_compatibility(
        n_types=4,
        structure='clustered',
        T=200,
        seed=42
    )
    
    print("\n6b. Core-Periphery Structure (5 types)")
    core_periphery_results = test_multitype_compatibility(
        n_types=5,
        structure='core_periphery',
        T=200,
        seed=42
    )
    
    # ===================================================================
    # 7. URGENCY-AWARE POLICIES
    # ===================================================================
    print("\n" + "=" * 70)
    print("7. URGENCY-AWARE POLICY EXPERIMENTS")
    print("=" * 70)
    
    print("\n7a. Short Deadlines (urgent market)")
    urgency_short = test_urgency_policies(avg_deadline=5.0, T=200, seed=42)
    
    print("\n7b. Long Deadlines (patient market)")
    urgency_long = test_urgency_policies(avg_deadline=20.0, T=200, seed=42)
    
    # ===================================================================
    # 8. CUSTOM EXPERIMENTS
    # ===================================================================
    print("\n" + "=" * 70)
    print("8. CUSTOM EXPERIMENT EXAMPLE")
    print("=" * 70)
    
    print("\nCustom 3-type system with asymmetric compatibility:")
    
    # Define custom types and compatibility
    custom_types = ['premium', 'standard', 'budget']
    custom_compat = {
        ('premium', 'premium'): 0.95,
        ('premium', 'standard'): 0.60,
        ('premium', 'budget'): 0.20,
        ('standard', 'standard'): 0.85,
        ('standard', 'budget'): 0.50,
        ('budget', 'budget'): 0.75,
    }
    
    custom_results = run_simulation(
        T=200,
        policy=Policy.GREEDY,
        compatibility_matrix=custom_compat,
        agent_types=custom_types,
        type_distribution=[0.2, 0.5, 0.3],  # 20% premium, 50% standard, 30% budget
        seed=42
    )
    
    print(f"\nOverall match rate: {custom_results['match_rate']:.3f}")
    print("Type-specific results:")
    for agent_type, metrics in sorted(custom_results['by_type'].items()):
        print(f"  {agent_type}: match_rate={metrics['match_rate']:.3f}, "
              f"avg_wait={metrics['avg_wait']:.2f}, count={metrics['total']}")
    
    # ===================================================================
    # SUMMARY
    # ===================================================================
    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("- GREEDY typically achieves highest match rates but may not maximize welfare")
    print("- PATIENT can improve welfare by waiting for better matches")
    print("- PATIENT_ALPHA offers a tunable trade-off (alpha ~ 0.3-0.5 often works well)")
    print("- URGENCY_AWARE and ADAPTIVE_ALPHA leverage deadline information")
    print("- Multi-type systems reveal richer matching dynamics")
    print("- Parameter sweeps help identify optimal operating regions")
    print("\nNext Steps:")
    print("- Experiment with different parameter combinations")
    print("- Design custom compatibility structures")
    print("- Extend to two-sided (rider-driver) markets")
    print("- Add spatial/geographic features")
    print("=" * 70)

if __name__ == "__main__":
    # Quick mode: just run baseline comparisons
    # Uncomment main() to run full demo
    
    print("Running baseline comparisons...")
    print("(Edit demo.py and call main() for full demo with plots)")
    print()
    run_baseline_comparisons(T=200, seed=42, verbose=True)
    
    # Full demo with all experiments and visualizations:
    # main()
