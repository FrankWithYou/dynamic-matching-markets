"""
Two-Sided Dynamic Matching Market Simulator (Uber-like)

This module extends the base simulator to support:
- Riders and drivers (two-sided market)
- Spatial locations and pickup distances
- Trip durations and driver reuse
- Time-varying demand/supply patterns
"""

import random
import math
import numpy as np
import matplotlib.pyplot as plt
from enum import Enum
from collections import defaultdict, deque
import heapq

# ============================================================================
# ENUMS AND CONSTANTS
# ============================================================================

class MatchingPolicy(Enum):
    GREEDY = 1          # Match closest available driver
    FCFS = 2            # First-come-first-served
    PATIENT = 3         # Wait until rider deadline urgent
    DISTANCE_AWARE = 4  # Balance distance and urgency
    BATCHING = 5        # Batch requests every T seconds

class LocationModel(Enum):
    LINE_1D = 1         # 1D line [0, L]
    GRID_2D = 2         # 2D grid [0,L] x [0,L]
    TWO_REGION = 3      # Two discrete regions

# ============================================================================
# CORE CLASSES
# ============================================================================

class Rider:
    """Rider requesting a trip."""
    _id_counter = 0
    
    def __init__(self, arrival_time, location, deadline, trip_distance=None,
                 patience_cost=0.1):
        self.id = Rider._id_counter
        Rider._id_counter += 1
        self.arrival_time = arrival_time
        self.location = location  # (x,) for 1D or (x,y) for 2D
        self.deadline = deadline
        self.patience_cost = patience_cost
        
        # Trip characteristics
        self.trip_distance = trip_distance  # can be None (sampled at match time)
        self.destination = None
        
        # Match tracking
        self.matched = False
        self.match_time = None
        self.driver_id = None
        self.pickup_time = None
        self.pickup_distance = None
        
    def is_expired(self, t):
        return t >= self.deadline
    
    def time_until_deadline(self, t):
        return max(0, self.deadline - t)
    
    def wait_time(self):
        if self.match_time is None:
            return None
        return self.match_time - self.arrival_time

class Driver:
    """Driver who can serve multiple trips."""
    _id_counter = 0
    
    def __init__(self, arrival_time, location):
        self.id = Driver._id_counter
        Driver._id_counter += 1
        self.arrival_time = arrival_time
        self.location = location
        
        # Status tracking
        self.status = 'idle'  # 'idle', 'picking_up', 'on_trip'
        self.available_at = arrival_time
        self.current_rider_id = None
        
        # Statistics
        self.trips_completed = 0
        self.total_idle_time = 0
        self.total_busy_time = 0
        self.total_distance_driven = 0
        
    def is_available(self, t):
        return t >= self.available_at and self.status == 'idle'
    
    def start_trip(self, t, rider, pickup_distance, trip_distance):
        """Start serving a rider."""
        self.status = 'on_trip'
        self.current_rider_id = rider.id
        pickup_time = pickup_distance  # assume speed = 1 unit/time
        trip_time = trip_distance
        self.available_at = t + pickup_time + trip_time
        self.total_distance_driven += pickup_distance + trip_distance
        return pickup_time, trip_time
    
    def complete_trip(self, t, dropoff_location):
        """Complete current trip and become idle at dropoff."""
        self.status = 'idle'
        self.location = dropoff_location
        self.current_rider_id = None
        self.trips_completed += 1

# ============================================================================
# SPATIAL UTILITIES
# ============================================================================

def distance(loc1, loc2, model=LocationModel.LINE_1D):
    """Calculate distance between two locations."""
    if model == LocationModel.LINE_1D:
        return abs(loc1[0] - loc2[0])
    elif model == LocationModel.GRID_2D:
        # Manhattan distance
        return abs(loc1[0] - loc2[0]) + abs(loc1[1] - loc2[1])
    elif model == LocationModel.TWO_REGION:
        # 0 if same region, fixed distance if different
        return 0.0 if loc1[0] == loc2[0] else 10.0
    return 0.0

def random_location(model=LocationModel.LINE_1D, bounds=10.0):
    """Generate random location based on model."""
    if model == LocationModel.LINE_1D:
        return (random.uniform(0, bounds),)
    elif model == LocationModel.GRID_2D:
        return (random.uniform(0, bounds), random.uniform(0, bounds))
    elif model == LocationModel.TWO_REGION:
        return (random.choice([0, 1]),)  # region 0 or 1
    return (0.0,)

def sample_destination(origin, model=LocationModel.LINE_1D, bounds=10.0,
                       avg_trip_distance=3.0):
    """Sample a destination given origin."""
    if model == LocationModel.LINE_1D:
        # Sample distance, ensure within bounds
        dist = np.random.exponential(avg_trip_distance)
        direction = random.choice([-1, 1])
        new_x = origin[0] + direction * dist
        new_x = max(0, min(bounds, new_x))
        return (new_x,)
    elif model == LocationModel.GRID_2D:
        # Sample in random direction
        angle = random.uniform(0, 2 * math.pi)
        dist = np.random.exponential(avg_trip_distance)
        new_x = origin[0] + dist * math.cos(angle)
        new_y = origin[1] + dist * math.sin(angle)
        new_x = max(0, min(bounds, new_x))
        new_y = max(0, min(bounds, new_y))
        return (new_x, new_y)
    elif model == LocationModel.TWO_REGION:
        # 70% stay in region, 30% go to other region
        if random.random() < 0.7:
            return origin
        else:
            return (1 - origin[0],)
    return origin

# ============================================================================
# TIME-VARYING DEMAND
# ============================================================================

def arrival_rate_function(t, base_rate=1.0, pattern='constant'):
    """Return arrival rate λ(t) at time t."""
    if pattern == 'constant':
        return base_rate
    elif pattern == 'rush_hour':
        # Two peaks: morning (t~50-100) and evening (t~300-350)
        # Assuming T represents hours, scaled appropriately
        hour = (t % 400) / 400 * 24  # map to 24-hour cycle
        if 7 <= hour <= 9 or 17 <= hour <= 19:  # rush hours
            return base_rate * 2.5
        elif 22 <= hour or hour <= 5:  # late night
            return base_rate * 0.3
        else:
            return base_rate
    elif pattern == 'sine_wave':
        # Smooth sinusoidal pattern
        return base_rate * (1 + 0.7 * math.sin(2 * math.pi * t / 200))
    return base_rate

def poisson_arrivals_time_varying(rate_func, T, pattern='constant'):
    """Generate arrivals with time-varying Poisson rate."""
    arrivals = []
    t = 0
    while t < T:
        current_rate = rate_func(t, pattern=pattern)
        if current_rate > 0:
            t += random.expovariate(current_rate)
        else:
            t += 1  # skip ahead if rate is 0
        if t <= T:
            arrivals.append(t)
    return arrivals

# ============================================================================
# MATCHING POLICIES
# ============================================================================

def greedy_spatial_match(riders, drivers, t, location_model=LocationModel.LINE_1D):
    """Match each rider to closest available driver (greedy)."""
    matches = []
    available_drivers = [d for d in drivers if d.is_available(t)]
    waiting_riders = [r for r in riders if not r.matched and not r.is_expired(t)]
    
    used_drivers = set()
    
    for rider in waiting_riders:
        # Find closest available driver
        best_driver = None
        best_distance = float('inf')
        
        for driver in available_drivers:
            if driver.id in used_drivers:
                continue
            dist = distance(rider.location, driver.location, location_model)
            if dist < best_distance:
                best_distance = dist
                best_driver = driver
        
        if best_driver is not None:
            matches.append((rider, best_driver, best_distance))
            used_drivers.add(best_driver.id)
    
    return matches

def fcfs_match(riders, drivers, t, location_model=LocationModel.LINE_1D,
               max_pickup_distance=5.0):
    """First-come-first-served: oldest rider gets first available driver."""
    matches = []
    available_drivers = [d for d in drivers if d.is_available(t)]
    waiting_riders = sorted([r for r in riders if not r.matched and not r.is_expired(t)],
                           key=lambda r: r.arrival_time)
    
    used_drivers = set()
    
    for rider in waiting_riders:
        # Find any available driver within max distance
        for driver in available_drivers:
            if driver.id in used_drivers:
                continue
            dist = distance(rider.location, driver.location, location_model)
            if dist <= max_pickup_distance:
                matches.append((rider, driver, dist))
                used_drivers.add(driver.id)
                break
    
    return matches

def distance_aware_match(riders, drivers, t, location_model=LocationModel.LINE_1D,
                        distance_weight=0.5):
    """Balance distance and urgency in matching."""
    matches = []
    available_drivers = [d for d in drivers if d.is_available(t)]
    waiting_riders = [r for r in riders if not r.matched and not r.is_expired(t)]
    
    if not waiting_riders or not available_drivers:
        return matches
    
    # Score-based matching
    used_drivers = set()
    
    for rider in waiting_riders:
        best_driver = None
        best_score = float('inf')
        
        urgency = 1.0 / (rider.time_until_deadline(t) + 0.1)
        
        for driver in available_drivers:
            if driver.id in used_drivers:
                continue
            
            dist = distance(rider.location, driver.location, location_model)
            # Lower score is better: weighted sum of distance and inverse urgency
            score = distance_weight * dist + (1 - distance_weight) * (1.0 / (urgency + 0.1))
            
            if score < best_score:
                best_score = score
                best_driver = driver
                best_distance = dist
        
        if best_driver is not None:
            matches.append((rider, best_driver, best_distance))
            used_drivers.add(best_driver.id)
    
    return matches

# ============================================================================
# EVENT-DRIVEN SIMULATION
# ============================================================================

class Event:
    """Simulation event."""
    def __init__(self, time, event_type, data=None):
        self.time = time
        self.event_type = event_type  # 'rider_arrival', 'driver_arrival', 'trip_complete'
        self.data = data
    
    def __lt__(self, other):
        return self.time < other.time

def run_uber_simulation(
    T=400,
    rider_arrival_rate=1.0,
    driver_arrival_rate=0.8,
    rider_pattern='constant',
    driver_pattern='constant',
    avg_deadline=15.0,
    avg_trip_distance=3.0,
    location_model=LocationModel.LINE_1D,
    location_bounds=10.0,
    policy=MatchingPolicy.GREEDY,
    matching_interval=0.5,  # how often to run matching
    seed=None
):
    """
    Run two-sided Uber-like simulation with spatial features.
    
    Returns:
        dict with comprehensive metrics
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    # Reset ID counters
    Rider._id_counter = 0
    Driver._id_counter = 0
    
    # Generate arrivals
    rider_times = poisson_arrivals_time_varying(
        lambda t, pattern: arrival_rate_function(t, rider_arrival_rate, pattern),
        T, rider_pattern
    )
    driver_times = poisson_arrivals_time_varying(
        lambda t, pattern: arrival_rate_function(t, driver_arrival_rate, pattern),
        T, driver_pattern
    )
    
    # Initialize event queue
    events = []
    
    # Add rider arrivals
    for t in rider_times:
        loc = random_location(location_model, location_bounds)
        deadline = t + random.expovariate(1.0 / avg_deadline)
        rider = Rider(t, loc, deadline)
        heapq.heappush(events, Event(t, 'rider_arrival', rider))
    
    # Add driver arrivals
    for t in driver_times:
        loc = random_location(location_model, location_bounds)
        driver = Driver(t, loc)
        heapq.heappush(events, Event(t, 'driver_arrival', driver))
    
    # Add matching events
    for t in np.arange(0, T, matching_interval):
        heapq.heappush(events, Event(t, 'matching', None))
    
    # Simulation state
    waiting_riders = []
    all_riders = []
    drivers = []
    all_drivers = []
    matches = []
    
    current_time = 0
    
    # Process events
    while events:
        event = heapq.heappop(events)
        current_time = event.time
        
        if current_time > T:
            break
        
        if event.event_type == 'rider_arrival':
            rider = event.data
            waiting_riders.append(rider)
            all_riders.append(rider)
        
        elif event.event_type == 'driver_arrival':
            driver = event.data
            drivers.append(driver)
            all_drivers.append(driver)
        
        elif event.event_type == 'trip_complete':
            driver = event.data
            dropoff_loc = driver.location  # already updated when trip started
            driver.complete_trip(current_time, dropoff_loc)
        
        elif event.event_type == 'matching':
            # Remove expired riders
            waiting_riders = [r for r in waiting_riders if not r.is_expired(current_time)]
            
            # Run matching policy
            if policy == MatchingPolicy.GREEDY:
                new_matches = greedy_spatial_match(waiting_riders, drivers,
                                                   current_time, location_model)
            elif policy == MatchingPolicy.FCFS:
                new_matches = fcfs_match(waiting_riders, drivers,
                                        current_time, location_model)
            elif policy == MatchingPolicy.DISTANCE_AWARE:
                new_matches = distance_aware_match(waiting_riders, drivers,
                                                   current_time, location_model)
            else:
                new_matches = greedy_spatial_match(waiting_riders, drivers,
                                                   current_time, location_model)
            
            # Process matches
            for rider, driver, pickup_distance in new_matches:
                # Mark rider as matched
                rider.matched = True
                rider.match_time = current_time
                rider.driver_id = driver.id
                rider.pickup_distance = pickup_distance
                
                # Sample trip distance and destination
                trip_distance = np.random.exponential(avg_trip_distance)
                destination = sample_destination(rider.location, location_model,
                                               location_bounds, avg_trip_distance)
                rider.destination = destination
                rider.trip_distance = trip_distance
                
                # Update driver
                pickup_time, trip_time = driver.start_trip(current_time, rider,
                                                          pickup_distance, trip_distance)
                rider.pickup_time = pickup_time
                
                # Update driver location to dropoff
                driver.location = destination
                
                # Schedule trip completion
                completion_time = current_time + pickup_time + trip_time
                heapq.heappush(events, Event(completion_time, 'trip_complete', driver))
                
                matches.append((rider, driver, current_time))
            
            # Remove matched riders
            matched_ids = {r.id for r, _, _ in new_matches}
            waiting_riders = [r for r in waiting_riders if r.id not in matched_ids]
    
    # Compute metrics
    return compute_uber_metrics(all_riders, all_drivers, matches, T, location_model)

def compute_uber_metrics(riders, drivers, matches, T, location_model):
    """Compute comprehensive metrics for Uber simulation."""
    matched_riders = [r for r in riders if r.matched]
    unmatched_riders = [r for r in riders if not r.matched]
    
    metrics = {
        'total_riders': len(riders),
        'total_drivers': len(drivers),
        'matched_riders': len(matched_riders),
        'unmatched_riders': len(unmatched_riders),
        'rider_match_rate': len(matched_riders) / len(riders) if riders else 0,
    }
    
    # Rider metrics
    if matched_riders:
        metrics['avg_rider_wait'] = np.mean([r.wait_time() for r in matched_riders])
        metrics['avg_pickup_distance'] = np.mean([r.pickup_distance for r in matched_riders])
        metrics['avg_pickup_time'] = np.mean([r.pickup_time for r in matched_riders])
        metrics['avg_trip_distance'] = np.mean([r.trip_distance for r in matched_riders])
    else:
        metrics['avg_rider_wait'] = 0
        metrics['avg_pickup_distance'] = 0
        metrics['avg_pickup_time'] = 0
        metrics['avg_trip_distance'] = 0
    
    # Driver metrics
    if drivers:
        metrics['avg_trips_per_driver'] = np.mean([d.trips_completed for d in drivers])
        metrics['avg_driver_distance'] = np.mean([d.total_distance_driven for d in drivers])
        
        # Driver utilization
        total_possible_time = sum(T - d.arrival_time for d in drivers)
        total_busy_time = sum(max(0, d.available_at - d.arrival_time) for d in drivers)
        metrics['driver_utilization'] = total_busy_time / total_possible_time if total_possible_time > 0 else 0
    else:
        metrics['avg_trips_per_driver'] = 0
        metrics['avg_driver_distance'] = 0
        metrics['driver_utilization'] = 0
    
    # Supply-demand balance
    metrics['supply_demand_ratio'] = len(drivers) / len(riders) if riders else 0
    
    return metrics

# ============================================================================
# EXPERIMENTS AND VISUALIZATION
# ============================================================================

def compare_uber_policies(T=400, seed=42):
    """Compare different matching policies in Uber setting."""
    print("=" * 70)
    print("UBER-LIKE MARKET: POLICY COMPARISON")
    print("=" * 70)
    
    policies = [
        MatchingPolicy.GREEDY,
        MatchingPolicy.FCFS,
        MatchingPolicy.DISTANCE_AWARE
    ]
    
    results = {}
    for policy in policies:
        print(f"\n{policy.name}:")
        res = run_uber_simulation(
            T=T,
            rider_arrival_rate=1.0,
            driver_arrival_rate=0.8,
            location_model=LocationModel.GRID_2D,
            policy=policy,
            seed=seed
        )
        results[policy.name] = res
        
        print(f"  Rider match rate: {res['rider_match_rate']:.1%}")
        print(f"  Avg wait time: {res['avg_rider_wait']:.2f}")
        print(f"  Avg pickup distance: {res['avg_pickup_distance']:.2f}")
        print(f"  Driver utilization: {res['driver_utilization']:.1%}")
        print(f"  Avg trips/driver: {res['avg_trips_per_driver']:.1f}")
    
    return results

def test_time_varying_demand(T=400, seed=42):
    """Test performance under time-varying demand patterns."""
    print("\n" + "=" * 70)
    print("TIME-VARYING DEMAND EXPERIMENT")
    print("=" * 70)
    
    patterns = ['constant', 'rush_hour', 'sine_wave']
    results = {}
    
    for pattern in patterns:
        print(f"\n{pattern.upper()} pattern:")
        res = run_uber_simulation(
            T=T,
            rider_arrival_rate=1.0,
            driver_arrival_rate=0.8,
            rider_pattern=pattern,
            driver_pattern='constant',
            location_model=LocationModel.GRID_2D,
            policy=MatchingPolicy.GREEDY,
            seed=seed
        )
        results[pattern] = res
        
        print(f"  Rider match rate: {res['rider_match_rate']:.1%}")
        print(f"  Avg wait time: {res['avg_rider_wait']:.2f}")
        print(f"  Driver utilization: {res['driver_utilization']:.1%}")
    
    return results

def test_supply_demand_balance(T=400, seed=42):
    """Test different supply-demand ratios."""
    print("\n" + "=" * 70)
    print("SUPPLY-DEMAND BALANCE EXPERIMENT")
    print("=" * 70)
    
    ratios = [0.5, 0.7, 0.9, 1.1, 1.3]  # driver/rider ratio
    results = []
    
    for ratio in ratios:
        res = run_uber_simulation(
            T=T,
            rider_arrival_rate=1.0,
            driver_arrival_rate=ratio * 1.0,
            location_model=LocationModel.LINE_1D,
            policy=MatchingPolicy.GREEDY,
            seed=seed
        )
        results.append(res)
        print(f"\nDriver/Rider ratio: {ratio:.1f}")
        print(f"  Match rate: {res['rider_match_rate']:.1%}")
        print(f"  Avg wait: {res['avg_rider_wait']:.2f}")
        print(f"  Driver util: {res['driver_utilization']:.1%}")
    
    # Plot
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 3, 1)
    plt.plot(ratios, [r['rider_match_rate'] for r in results], 'o-')
    plt.xlabel('Supply/Demand Ratio')
    plt.ylabel('Rider Match Rate')
    plt.title('Match Rate vs Supply')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 3, 2)
    plt.plot(ratios, [r['avg_rider_wait'] for r in results], 'o-', color='orange')
    plt.xlabel('Supply/Demand Ratio')
    plt.ylabel('Avg Wait Time')
    plt.title('Wait Time vs Supply')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 3, 3)
    plt.plot(ratios, [r['driver_utilization'] for r in results], 'o-', color='green')
    plt.xlabel('Supply/Demand Ratio')
    plt.ylabel('Driver Utilization')
    plt.title('Utilization vs Supply')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    return results

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("TWO-SIDED UBER-LIKE MARKET SIMULATOR")
    print()
    
    # Basic comparison
    compare_uber_policies(T=400, seed=42)
    
    # Time-varying demand
    # test_time_varying_demand(T=400, seed=42)
    
    # Supply-demand balance (with plots)
    # test_supply_demand_balance(T=400, seed=42)
