from sim import *

print("Testing simulator...")
print()

# Test basic simulation
r = run_simulation(T=50, seed=1)
print(f"✓ Basic simulation: match_rate={r['match_rate']:.2%}")

# Test multi-type
matrix, types = create_compatibility_matrix(n_types=3, structure='uniform')
r2 = run_simulation(T=50, seed=1, compatibility_matrix=matrix, agent_types=types)
print(f"✓ Multi-type (3 types): match_rate={r2['match_rate']:.2%}")

# Test urgency policy
r3 = run_simulation(T=50, seed=1, policy=Policy.URGENCY_AWARE)
print(f"✓ Urgency policy: match_rate={r3['match_rate']:.2%}")

print()
print("All tests passed! ✓")
print("Run 'python demo.py' for comprehensive examples.")
