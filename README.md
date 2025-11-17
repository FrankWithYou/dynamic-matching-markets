# Dynamic Matching Markets Simulator
Dynamic market matching simulator for CS 580 at UIUC

A comprehensive simulator for studying dynamic matching markets with Poisson arrivals, agent heterogeneity, and various matching policies.

## Features

### Core Mechanics
- **Poisson Arrivals**: Agents arrive according to a Poisson process
- **Deadlines**: Each agent has a random deadline (patience/lifetime)
- **Agent Types**: Support for arbitrary number of agent types with configurable compatibility
- **Waiting Costs**: Agents incur costs while waiting to be matched
- **Compatibility**: Stochastic compatibility between agent pairs

### Matching Policies

1. **GREEDY**: Match as soon as possible (myopic matching)
2. **PATIENT**: Only match agents when their deadlines are expiring
3. **PATIENT_ALPHA**: Randomized mix of GREEDY and PATIENT (α controls greediness)
4. **URGENCY_AWARE**: Prioritize matching high-urgency agents first
5. **ADAPTIVE_ALPHA**: Dynamically adjust greediness based on pool urgency

### Compatibility Models

- **2-Type System** (default): "easy" and "hard" agents with different match probabilities
- **Multi-Type System**: Support for N agent types with custom compatibility matrices
- **Compatibility Structures**:
  - **Uniform**: All type pairs have similar probabilities
  - **Clustered**: Types form clusters; high within-cluster, low across-cluster matching
  - **Core-Periphery**: Universal donor type + periphery types

### Metrics & Analytics

**Overall Metrics:**
- Match rate (proportion of agents matched)
- Average waiting time
- Total welfare (value minus waiting costs)

**Type-Specific Metrics:**
- Match rates by agent type
- Average waiting times by type
- Welfare contribution by type
- Expired/unmatched rates by type

## Quick Start

```bash
# Run basic simulations
python sim.py

# Run demo with various experiments
python demo.py
```

## Usage Examples

See `demo.py` for comprehensive examples including:
- Baseline policy comparisons
- Parameter sweeps and heatmaps
- Multi-type compatibility experiments
- Urgency-aware policy testing

## Recent Improvements

### Fixed Issues
1. **PATIENT Policy Bug**: Fixed event loop ordering so expiring agents get a chance to match
2. **Reproducibility**: Added seed parameter for consistent results

### Enhanced Features
1. **Type-Specific Metrics**: Track performance separately for each agent type
2. **Flexible Type System**: Support for arbitrary number of agent types
3. **Compatibility Matrices**: Configurable structures (uniform, clustered, core-periphery)
4. **Urgency Policies**: New policies that leverage deadline information
5. **Structured Experiments**: Helper functions for common workflows
6. **Parameter Sweeps**: Systematic parameter space exploration with visualization
7. **Heatmap Analysis**: 2D parameter space visualization

## Key Functions

### Running Simulations
- `run_simulation()` - Main simulation function
- `run_baseline_comparisons()` - Compare policies on standard markets
- `run_heterogeneity_experiments()` - Test across market compositions
- `test_multitype_compatibility()` - Test N-type systems
- `test_urgency_policies()` - Compare urgency-aware policies

### Analysis & Visualization
- `plot_parameter_sweep()` - Sweep one parameter for multiple policies
- `plot_alpha_sweep()` - Alpha parameter sweep for PATIENT_ALPHA
- `generate_heatmap()` - 2D parameter space visualization

### Compatibility
- `create_compatibility_matrix()` - Generate N-type compatibility matrices
- `are_compatible()` - Check if two agents can match

## Next Steps: Toward Two-Sided Markets

The codebase is ready for extension to Uber-like markets with:
1. **Two-Sided Roles**: Separate rider and driver agents
2. **Geography**: Add locations and pickup distances  
3. **Driver Reuse**: Drivers complete trips and re-enter idle pool
4. **Time-Varying Demand**: Rush hour vs off-peak patterns

## Files

- `sim.py` - Main simulator with all policies and analysis functions
- `demo.py` - Example usage and experiments
- `README.md` - This file
