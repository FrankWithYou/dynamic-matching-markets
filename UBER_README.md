# Two-Sided Uber-Like Market Simulator

Extension of the base simulator implementing spatial, two-sided matching markets with driver reuse and time-varying demand patterns.

## Overview

This simulator models ride-hailing platforms like Uber/Lyft with:
- **Two-sided market**: Separate rider and driver populations
- **Spatial locations**: 1D, 2D, or two-region geography
- **Driver reuse**: Drivers complete trips and return to the idle pool
- **Trip durations**: Realistic pickup and travel times
- **Time-varying demand**: Rush hour patterns and temporal dynamics
- **Event-driven simulation**: Efficient handling of arrivals and completions

## Key Features

### Agents

**Riders:**
- Single trip request
- Arrival time and location
- Deadline (patience limit)
- Assigned driver and pickup details

**Drivers:**
- Can serve multiple trips sequentially
- Tracked through idle → picking up → on trip → idle cycle
- Location updates after each trip
- Cumulative statistics (trips, distance, utilization)

### Spatial Models

1. **LINE_1D**: One-dimensional line [0, L]
   - Simple linear distance
   - Good for highways, corridors

2. **GRID_2D**: Two-dimensional grid [0,L] × [0,L]
   - Manhattan distance
   - Realistic city modeling

3. **TWO_REGION**: Discrete regions (e.g., city/suburbs)
   - Binary location
   - Inter-region distance penalty
   - Captures urban/suburban dynamics

### Matching Policies

1. **GREEDY**: Match each rider to closest available driver
   - Minimizes pickup distance
   - Rider-optimal

2. **FCFS**: First-come-first-served
   - Fairness priority
   - May increase pickup distances

3. **DISTANCE_AWARE**: Balance distance and urgency
   - Weighted scoring function
   - Configurable trade-offs

### Time-Varying Demand

**Patterns:**
- `constant`: Steady arrival rate
- `rush_hour`: Morning (7-9am) and evening (5-7pm) peaks
- `sine_wave`: Smooth sinusoidal variation

**Usage:**
```python
run_uber_simulation(
    rider_pattern='rush_hour',
    driver_pattern='constant',
    ...
)
```

## Quick Start

### Basic Simulation

```python
from uber_sim import *

# Run simple simulation
results = run_uber_simulation(
    T=400,
    rider_arrival_rate=1.0,
    driver_arrival_rate=0.8,
    location_model=LocationModel.GRID_2D,
    policy=MatchingPolicy.GREEDY,
    seed=42
)

print(f"Match rate: {results['rider_match_rate']:.1%}")
print(f"Avg wait: {results['avg_rider_wait']:.2f}")
print(f"Driver utilization: {results['driver_utilization']:.1%}")
```

### Policy Comparison

```python
# Compare all policies
compare_uber_policies(T=400, seed=42)
```

### Time-Varying Demand

```python
# Test rush hour patterns
test_time_varying_demand(T=400, seed=42)
```

### Supply-Demand Analysis

```python
# With visualization
test_supply_demand_balance(T=400, seed=42)
```

## Parameters

### Core Parameters

| Parameter | Description | Typical Range |
|-----------|-------------|---------------|
| `T` | Simulation horizon | 200-500 |
| `rider_arrival_rate` | Rider Poisson rate (λ) | 0.5-2.0 |
| `driver_arrival_rate` | Driver Poisson rate | 0.3-1.5 |
| `avg_deadline` | Average rider patience | 10-30 |
| `avg_trip_distance` | Average trip length | 2-5 |
| `location_bounds` | Spatial domain size | 10-50 |
| `matching_interval` | How often to run matching | 0.1-1.0 |

### Pattern Parameters

- `rider_pattern`: `'constant'`, `'rush_hour'`, `'sine_wave'`
- `driver_pattern`: Same options
- `location_model`: `LocationModel.LINE_1D`, `GRID_2D`, `TWO_REGION`
- `policy`: `MatchingPolicy.GREEDY`, `FCFS`, `DISTANCE_AWARE`

## Metrics

### Rider Metrics
- `rider_match_rate`: Fraction of riders matched
- `avg_rider_wait`: Average wait time until matched
- `avg_pickup_distance`: Average driver distance to rider
- `avg_pickup_time`: Average time until driver arrives
- `avg_trip_distance`: Average trip length

### Driver Metrics
- `avg_trips_per_driver`: Average completed trips per driver
- `avg_driver_distance`: Average total distance driven
- `driver_utilization`: Fraction of time drivers are busy
- `supply_demand_ratio`: Driver/rider ratio

### System Metrics
- `total_riders`: Total rider arrivals
- `total_drivers`: Total driver arrivals
- `matched_riders`: Number of successful matches
- `unmatched_riders`: Number of riders who expired

## Example Experiments

### 1. Impact of Driver Supply

```python
# How does driver/rider ratio affect performance?
for ratio in [0.5, 0.7, 0.9, 1.1, 1.3]:
    results = run_uber_simulation(
        T=400,
        rider_arrival_rate=1.0,
        driver_arrival_rate=ratio,
        seed=42
    )
    print(f"Ratio {ratio}: match_rate={results['rider_match_rate']:.1%}")
```

### 2. Rush Hour Dynamics

```python
# Compare constant vs rush hour demand
results_constant = run_uber_simulation(
    rider_pattern='constant',
    seed=42
)

results_rush = run_uber_simulation(
    rider_pattern='rush_hour',
    seed=42
)
```

### 3. Spatial Structure Effects

```python
# How does geography affect matching?
for model in [LocationModel.LINE_1D, LocationModel.GRID_2D]:
    results = run_uber_simulation(
        location_model=model,
        seed=42
    )
    print(f"{model.name}: pickup_dist={results['avg_pickup_distance']:.2f}")
```

### 4. Driver Reuse Analysis

```python
# Low supply → high reuse
results_low = run_uber_simulation(
    driver_arrival_rate=0.5,
    avg_trip_distance=3.0,
    seed=42
)
print(f"Trips per driver: {results_low['avg_trips_per_driver']:.2f}")

# High supply → low reuse
results_high = run_uber_simulation(
    driver_arrival_rate=1.2,
    avg_trip_distance=3.0,
    seed=42
)
print(f"Trips per driver: {results_high['avg_trips_per_driver']:.2f}")
```

## Architecture

### Event-Driven Simulation

Uses priority queue (heapq) for efficient event processing:

**Event Types:**
1. `rider_arrival`: New rider enters market
2. `driver_arrival`: New driver enters market
3. `matching`: Run matching algorithm
4. `trip_complete`: Driver finishes trip, returns to idle

**Event Loop:**
```
while events:
    event = heappop(events)
    if event.type == 'rider_arrival':
        add_to_waiting_pool()
    elif event.type == 'matching':
        matches = run_matching_policy()
        schedule_trip_completions()
    elif event.type == 'trip_complete':
        driver.status = 'idle'
        driver.location = dropoff
```

### Driver Lifecycle

```
arrival → idle → matched → picking_up → on_trip → complete → idle → ...
```

Each trip updates:
- Driver location (to dropoff)
- Trip count
- Total distance driven
- Availability time

## Research Applications

### Questions You Can Study

1. **Supply-Demand Balance**:
   - Optimal driver/rider ratio
   - Effects of over/under-supply

2. **Spatial Dynamics**:
   - Local shortages after demand spikes
   - Benefits of driver repositioning
   - Urban vs suburban service quality

3. **Temporal Patterns**:
   - Rush hour surge dynamics
   - Time-of-day pricing implications
   - Demand prediction importance

4. **Policy Design**:
   - FCFS vs distance-minimizing
   - Fairness vs efficiency trade-offs
   - Urgency-aware matching

5. **System Efficiency**:
   - Driver utilization optimization
   - Trip distance vs throughput
   - Batching/pooling benefits

## Comparison to Base Simulator

| Feature | Base (`sim.py`) | Uber (`uber_sim.py`) |
|---------|----------------|----------------------|
| Market type | One-sided | Two-sided |
| Agent reuse | No | Yes (drivers) |
| Geography | None | 1D/2D/Regions |
| Spatial matching | N/A | Distance-based |
| Trip completion | Immediate | Event-driven |
| Demand patterns | Constant | Time-varying |
| Key metric | Match rate | Match rate + utilization |

## Limitations & Extensions

### Current Limitations
- No surge pricing
- No driver repositioning
- No trip pooling/batching
- Simplified trip distance model
- No traffic/congestion effects

### Potential Extensions
1. **Surge Pricing**: Dynamic price adjustment based on supply/demand
2. **Repositioning**: Drivers move to high-demand areas when idle
3. **Pooling**: Multiple riders share trips
4. **Heterogeneous Drivers**: Different vehicle types/capacities
5. **Route Optimization**: Multi-stop optimization
6. **Congestion**: Speed/distance affected by traffic
7. **Preferences**: Rider/driver preferences and ratings

## Files

- `uber_sim.py` - Main two-sided simulator
- `uber_demo.py` - Comprehensive demonstration script
- `UBER_README.md` - This file

## Running Experiments

```bash
# Basic policy comparison
python uber_sim.py

# Comprehensive demo
python uber_demo.py

# Custom experiments
python
>>> from uber_sim import *
>>> # Your experiments here
```

## Performance

- Event-driven: O(n log n) for n events
- Matching: O(r × d) for r riders, d drivers per matching interval
- Memory: Linear in agents + events
- Typical runtime: <5s for T=400

## References

See main `README.md` for general dynamic matching references.

Uber-specific concepts:
- Spatial matching markets
- Driver repositioning
- Surge pricing mechanisms
- Ride-sharing/pooling algorithms
