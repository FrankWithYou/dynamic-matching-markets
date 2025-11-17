# Quick Reference Guide

## Running Simulations

### Basic Simulation
```python
from sim import *

# Single simulation with default parameters
results = run_simulation(T=200, seed=42)
print(f"Match rate: {results['match_rate']:.2%}")
```

### Compare All Policies
```python
# Basic comparison
run_baseline_comparisons(T=200, seed=42)

# Include urgency-aware policies
run_baseline_comparisons(T=200, seed=42, include_urgency=True)
```

## Parameter Sweeps

### Single Parameter
```python
# Sweep arrival rate (thin vs thick markets)
plot_parameter_sweep('arrival_rate', T=200, seed=42)

# Sweep deadline (patient vs impatient)
plot_parameter_sweep('avg_deadline', T=200, seed=42)

# Sweep market composition
plot_parameter_sweep('easy_fraction', T=200, seed=42)

# Alpha sweep for PATIENT_ALPHA
plot_alpha_sweep(easy_fraction=0.7, T=200, seed=42)
```

### 2D Heatmaps
```python
# Match rate heatmap
generate_heatmap(
    'arrival_rate', 'avg_deadline',
    policy=Policy.GREEDY,
    metric='match_rate',
    T=200, seed=42
)

# Welfare heatmap
generate_heatmap(
    'arrival_rate', 'easy_fraction',
    policy=Policy.PATIENT_ALPHA,
    metric='welfare',
    T=200, seed=42
)
```

## Multi-Type Systems

### Predefined Structures
```python
# Clustered types
test_multitype_compatibility(n_types=4, structure='clustered', T=200, seed=42)

# Core-periphery
test_multitype_compatibility(n_types=5, structure='core_periphery', T=200, seed=42)

# Uniform
matrix, types = create_compatibility_matrix(n_types=3, structure='uniform')
```

### Custom Compatibility
```python
# Define custom types
types = ['VIP', 'regular', 'budget']
compat = {
    ('VIP', 'VIP'): 0.95,
    ('VIP', 'regular'): 0.50,
    ('VIP', 'budget'): 0.10,
    ('regular', 'regular'): 0.85,
    ('regular', 'budget'): 0.60,
    ('budget', 'budget'): 0.80,
}

# Run simulation
results = run_simulation(
    T=200,
    compatibility_matrix=compat,
    agent_types=types,
    type_distribution=[0.1, 0.6, 0.3],
    seed=42
)
```

## Urgency Experiments

```python
# Compare urgency policies
test_urgency_policies(avg_deadline=10.0, T=200, seed=42)

# Test on urgent market
test_urgency_policies(avg_deadline=5.0, T=200, seed=42)

# Test on patient market
test_urgency_policies(avg_deadline=20.0, T=200, seed=42)
```

## Policy Enum Values

```python
Policy.GREEDY          # Match immediately
Policy.PATIENT         # Wait until deadlines
Policy.PATIENT_ALPHA   # Randomized mix (use alpha parameter)
Policy.URGENCY_AWARE   # Prioritize urgent agents
Policy.ADAPTIVE_ALPHA  # Dynamic greediness
```

## Key Parameters

| Parameter | Description | Typical Range |
|-----------|-------------|---------------|
| `T` | Simulation horizon | 100-500 |
| `arrival_rate` | Poisson rate (λ) | 0.5-3.0 |
| `easy_fraction` | Proportion of easy agents | 0.0-1.0 |
| `avg_deadline` | Average agent patience | 5-30 |
| `alpha` | Greediness (for PATIENT_ALPHA) | 0.0-1.0 |
| `seed` | Random seed | Any integer |

## Result Structure

```python
results = {
    'match_rate': 0.89,        # Overall match rate
    'avg_wait': 2.5,           # Average wait time
    'welfare': 150.0,          # Total welfare
    'matched': 178,            # Number matched
    'unmatched': 22,           # Number unmatched
    'total': 200,              # Total agents
    'by_type': {               # Type-specific metrics
        'easy': {
            'match_rate': 0.92,
            'avg_wait': 2.1,
            'welfare': 120.0,
            'matched': 160,
            'unmatched': 15,
            'total': 175,
            'expired_unmatched_rate': 0.08
        },
        'hard': { ... }
    }
}
```

## Common Workflows

### 1. Explore New Market Settings
```python
# Start with baseline
run_baseline_comparisons(T=200, seed=42)

# Test heterogeneity
run_heterogeneity_experiments(T=200, seed=42)

# Sweep key parameters
plot_parameter_sweep('arrival_rate', T=200, seed=42)
```

### 2. Tune Policy Parameters
```python
# Find optimal alpha
plot_alpha_sweep(easy_fraction=0.7, T=200, seed=42)

# Test across market types
for ef in [0.3, 0.5, 0.7, 0.9]:
    plot_alpha_sweep(easy_fraction=ef, T=200, seed=42)
```

### 3. Research Questions
```python
# Q: How does PATIENT perform in thin vs thick markets?
plot_parameter_sweep(
    'arrival_rate',
    policies=[Policy.PATIENT],
    param_values=[0.5, 1.0, 2.0, 3.0],
    T=200, seed=42
)

# Q: When do urgency-aware policies help?
for deadline in [5, 10, 20]:
    test_urgency_policies(avg_deadline=deadline, T=200, seed=42)
```

## Tips & Best Practices

1. **Always use seeds** for reproducible experiments
2. **Start with T=200** for fast iteration, increase for final results
3. **Compare policies on same seed** for fair comparison
4. **Check type-specific metrics** (`results['by_type']`) for insights
5. **Use heatmaps** to explore 2D parameter spaces efficiently
6. **Save plots** with `save_fig=True` parameter

## Troubleshooting

### Plots not showing
```python
# Add at the end of your script
plt.show()
```

### Low match rates
- Increase arrival_rate (thicker market)
- Increase compatibility probabilities
- Use GREEDY instead of PATIENT

### High computational time
- Reduce T (simulation horizon)
- Reduce grid resolution in heatmaps
- Use fewer parameter values in sweeps

## Example Research Workflow

```python
# 1. Setup
from sim import *
import matplotlib.pyplot as plt

SEED = 42
T = 200

# 2. Baseline
print("Running baseline...")
run_baseline_comparisons(T=T, seed=SEED)

# 3. Parameter exploration
print("\nExploring arrival rate...")
plot_parameter_sweep('arrival_rate', T=T, seed=SEED)

# 4. Focused analysis
print("\nTesting multi-type system...")
test_multitype_compatibility(
    n_types=4, 
    structure='clustered',
    T=T, 
    seed=SEED
)

# 5. Heatmap
print("\nGenerating heatmap...")
generate_heatmap(
    'arrival_rate', 'avg_deadline',
    policy=Policy.PATIENT_ALPHA,
    metric='welfare',
    T=T, seed=SEED
)

print("\nDone!")
```

## Getting Help

- See `README.md` for comprehensive documentation
- See `IMPROVEMENTS.md` for technical details
- Run `demo.py` for complete examples
- Read docstrings: `help(run_simulation)`
