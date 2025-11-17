"""
Demo script for Two-Sided Uber-Like Market Simulator

Demonstrates spatial matching, driver reuse, and time-varying demand.
"""

from uber_sim import *

def main():
    print("=" * 70)
    print("TWO-SIDED UBER-LIKE MARKET SIMULATOR - COMPREHENSIVE DEMO")
    print("=" * 70)
    
    SEED = 42
    T = 400
    
    # ========================================================================
    # 1. BASIC POLICY COMPARISON
    # ========================================================================
    print("\n" + "=" * 70)
    print("1. MATCHING POLICY COMPARISON")
    print("=" * 70)
    print("\nComparing spatial matching policies...")
    
    results1 = compare_uber_policies(T=T, seed=SEED)
    
    # ========================================================================
    # 2. LOCATION MODELS
    # ========================================================================
    print("\n" + "=" * 70)
    print("2. LOCATION MODEL COMPARISON")
    print("=" * 70)
    
    location_models = [
        (LocationModel.LINE_1D, "1D Line"),
        (LocationModel.GRID_2D, "2D Grid"),
        (LocationModel.TWO_REGION, "Two Regions")
    ]
    
    for model, name in location_models:
        print(f"\n{name}:")
        res = run_uber_simulation(
            T=T,
            rider_arrival_rate=1.0,
            driver_arrival_rate=0.8,
            location_model=model,
            policy=MatchingPolicy.GREEDY,
            seed=SEED
        )
        print(f"  Match rate: {res['rider_match_rate']:.1%}")
        print(f"  Avg wait: {res['avg_rider_wait']:.2f}")
        print(f"  Avg pickup distance: {res['avg_pickup_distance']:.2f}")
        print(f"  Driver utilization: {res['driver_utilization']:.1%}")
    
    # ========================================================================
    # 3. TIME-VARYING DEMAND
    # ========================================================================
    results2 = test_time_varying_demand(T=T, seed=SEED)
    
    # ========================================================================
    # 4. SUPPLY-DEMAND BALANCE
    # ========================================================================
    print("\n" + "=" * 70)
    print("4. SUPPLY-DEMAND BALANCE ANALYSIS")
    print("=" * 70)
    print("\nHow does driver supply affect system performance?")
    print("(Close plot window to continue)\n")
    
    results3 = test_supply_demand_balance(T=T, seed=SEED)
    
    # ========================================================================
    # 5. RUSH HOUR PATTERNS
    # ========================================================================
    print("\n" + "=" * 70)
    print("5. RUSH HOUR VS OFF-PEAK COMPARISON")
    print("=" * 70)
    
    print("\nConstant supply, rush hour demand:")
    res_rush = run_uber_simulation(
        T=T,
        rider_arrival_rate=1.0,
        driver_arrival_rate=0.8,
        rider_pattern='rush_hour',
        driver_pattern='constant',
        location_model=LocationModel.GRID_2D,
        policy=MatchingPolicy.GREEDY,
        seed=SEED
    )
    print(f"  Match rate: {res_rush['rider_match_rate']:.1%}")
    print(f"  Avg wait: {res_rush['avg_rider_wait']:.2f}")
    print(f"  Driver utilization: {res_rush['driver_utilization']:.1%}")
    
    print("\nMatched supply (rush hour for both):")
    res_matched = run_uber_simulation(
        T=T,
        rider_arrival_rate=1.0,
        driver_arrival_rate=0.8,
        rider_pattern='rush_hour',
        driver_pattern='rush_hour',
        location_model=LocationModel.GRID_2D,
        policy=MatchingPolicy.GREEDY,
        seed=SEED
    )
    print(f"  Match rate: {res_matched['rider_match_rate']:.1%}")
    print(f"  Avg wait: {res_matched['avg_rider_wait']:.2f}")
    print(f"  Driver utilization: {res_matched['driver_utilization']:.1%}")
    
    # ========================================================================
    # 6. DRIVER REUSE ANALYSIS
    # ========================================================================
    print("\n" + "=" * 70)
    print("6. DRIVER REUSE & TRIP COMPLETION")
    print("=" * 70)
    
    print("\nLow driver supply (more reuse):")
    res_low = run_uber_simulation(
        T=T,
        rider_arrival_rate=1.0,
        driver_arrival_rate=0.5,
        avg_trip_distance=3.0,
        location_model=LocationModel.LINE_1D,
        policy=MatchingPolicy.GREEDY,
        seed=SEED
    )
    print(f"  Avg trips per driver: {res_low['avg_trips_per_driver']:.2f}")
    print(f"  Driver utilization: {res_low['driver_utilization']:.1%}")
    print(f"  Match rate: {res_low['rider_match_rate']:.1%}")
    
    print("\nHigh driver supply (less reuse):")
    res_high = run_uber_simulation(
        T=T,
        rider_arrival_rate=1.0,
        driver_arrival_rate=1.2,
        avg_trip_distance=3.0,
        location_model=LocationModel.LINE_1D,
        policy=MatchingPolicy.GREEDY,
        seed=SEED
    )
    print(f"  Avg trips per driver: {res_high['avg_trips_per_driver']:.2f}")
    print(f"  Driver utilization: {res_high['driver_utilization']:.1%}")
    print(f"  Match rate: {res_high['rider_match_rate']:.1%}")
    
    # ========================================================================
    # 7. SPATIAL DYNAMICS
    # ========================================================================
    print("\n" + "=" * 70)
    print("7. SPATIAL EFFECTS: TRIP DISTANCE IMPACT")
    print("=" * 70)
    
    trip_distances = [1.0, 3.0, 5.0]
    
    for dist in trip_distances:
        res = run_uber_simulation(
            T=T,
            rider_arrival_rate=1.0,
            driver_arrival_rate=0.8,
            avg_trip_distance=dist,
            location_model=LocationModel.GRID_2D,
            policy=MatchingPolicy.GREEDY,
            seed=SEED
        )
        print(f"\nAvg trip distance = {dist:.1f}:")
        print(f"  Match rate: {res['rider_match_rate']:.1%}")
        print(f"  Avg pickup distance: {res['avg_pickup_distance']:.2f}")
        print(f"  Driver utilization: {res['driver_utilization']:.1%}")
        print(f"  Trips per driver: {res['avg_trips_per_driver']:.2f}")
    
    # ========================================================================
    # 8. POLICY COMPARISON WITH SPATIAL CONSTRAINTS
    # ========================================================================
    print("\n" + "=" * 70)
    print("8. POLICY COMPARISON: TWO-REGION MARKET")
    print("=" * 70)
    print("\nTesting policies in a two-region market (e.g., city + suburbs)...")
    
    policies = [MatchingPolicy.GREEDY, MatchingPolicy.DISTANCE_AWARE]
    
    for policy in policies:
        res = run_uber_simulation(
            T=T,
            rider_arrival_rate=1.0,
            driver_arrival_rate=0.8,
            location_model=LocationModel.TWO_REGION,
            policy=policy,
            seed=SEED
        )
        print(f"\n{policy.name}:")
        print(f"  Match rate: {res['rider_match_rate']:.1%}")
        print(f"  Avg wait: {res['avg_rider_wait']:.2f}")
        print(f"  Avg pickup distance: {res['avg_pickup_distance']:.2f}")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 70)
    print("DEMO COMPLETE - KEY INSIGHTS")
    print("=" * 70)
    print("""
Key Findings from Uber-Like Market Simulation:

1. SPATIAL MATCHING:
   - GREEDY minimizes pickup distances (match to closest driver)
   - FCFS may increase pickup distances but treats riders fairly
   - DISTANCE_AWARE balances proximity and urgency

2. DRIVER REUSE:
   - Drivers complete trips and re-enter at dropoff location
   - Low supply → high utilization, more trips per driver
   - High supply → low utilization, fewer trips per driver

3. TIME-VARYING DEMAND:
   - Rush hour creates surge demand
   - Mismatched supply/demand → lower match rates, higher wait times
   - Matched patterns → better performance

4. SUPPLY-DEMAND BALANCE:
   - Match rate increases with driver supply (up to ~100%)
   - Wait time decreases with more drivers
   - Driver utilization decreases with over-supply

5. SPATIAL STRUCTURE:
   - 1D: Linear distance, simple dynamics
   - 2D Grid: More realistic, Manhattan distance
   - Two regions: Captures urban/suburban asymmetries

6. TRIP DISTANCE:
   - Longer trips → drivers unavailable longer
   - Trade-off: serve nearby vs distant riders
   - Affects local supply imbalances

Research Directions:
- Surge pricing to balance supply/demand
- Driver repositioning strategies
- Batching/pooling for efficiency
- Fairness across geographic regions
- Dynamic policy adaptation to demand patterns
    """)
    print("=" * 70)

if __name__ == "__main__":
    # Quick demo: just policy comparison
    print("Running policy comparison...")
    print("(Edit uber_demo.py and uncomment main() for full demo)\n")
    
    compare_uber_policies(T=400, seed=42)
    
    # Full comprehensive demo:
    # main()
