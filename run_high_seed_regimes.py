"""
Run regime experiments with high number of seeds for robust statistical results.
"""

from regime_experiments import visualize_regime_comparison

if __name__ == "__main__":
    print("=" * 70)
    print("HIGH-SEED REGIME COMPARISON")
    print("Running with 50 seeds for robust statistical significance")
    print("=" * 70)
    print()
    
    # Run with 50 seeds (will take a few minutes)
    visualize_regime_comparison(T=200, seed=42, n_seeds=50, save_fig=True)
    
    print("\n" + "=" * 70)
    print("COMPLETED - Results saved to regime_comparison.png")
    print("=" * 70)
