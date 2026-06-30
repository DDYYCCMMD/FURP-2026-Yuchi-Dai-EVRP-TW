# Week 2 Baseline Method Comparison

This note supports the Week 2 lab task in [`labs/tasks/week02_works.md`](../labs/tasks/week02_works.md). The goal is to recreate baseline methods from the provided repositories, test them on representative problem scales, and reflect on how they relate to the target EVRP-TW project.

## Objective

Week 2 focuses on baseline recreation and comparison:

- Recreate the original POMO implementation from [`yd-kwon/POMO`](../labs/week2/pomo).
- Recreate the GA-based VRPTW implementation from [`py-ga-VRPTW`](../labs/week2/ga_evrptw).
- Record objective values, runtime, scale, and constraint coverage.
- Identify what still needs to be added for EVRP-TW, especially energy and charging constraints.

## Methods

### POMO Baseline

The POMO repository contains the paper implementation for:

- TSP: Traveling Salesman Problem
- CVRP: Capacitated Vehicle Routing Problem

The tested code is from:

- [`labs/week2/pomo/NEW_py_ver/TSP/POMO`](../labs/week2/pomo/NEW_py_ver/TSP/POMO)
- [`labs/week2/pomo/NEW_py_ver/CVRP/POMO`](../labs/week2/pomo/NEW_py_ver/CVRP/POMO)

The experiments used the provided pretrained checkpoints in debug CPU mode. This was done to verify the original baseline quickly without retraining thousands of epochs.

### GA Baseline

The GA baseline is the cloned VRPTW implementation from:

- [`labs/week2/ga_evrptw`](../labs/week2/ga_evrptw)

It represents a genetic algorithm approach for Solomon-style VRPTW instances. The solution is encoded as a customer permutation (`individual`) and decoded into vehicle routes according to capacity and route-time feasibility. Time-window effects are handled through waiting and delay penalties.

## Experiment Results

Runtime is reported using `/usr/bin/time -p`, using the `real` time.

| Method | Problem / Instance | Scale | Objective / Score | Runtime (s) | Constraint Coverage | Notes |
|---|---|---:|---:|---:|---|---|
| POMO-TSP | TSP20 | 20 nodes | NO-AUG `3.8146`, AUG `3.8139` | `2.44` | Distance only | Provided checkpoint, CPU debug mode |
| POMO-TSP | TSP100 | 100 nodes | NO-AUG `7.8014`, AUG `7.7858` | `22.41` | Distance only | Provided checkpoint, CPU debug mode |
| POMO-CVRP | CVRP100 | 100 customers | NO-AUG `15.6327`, AUG `15.5858` | `4.12` | Capacity | Provided checkpoint, CPU debug mode, 10 test episodes |
| GA-VRPTW | R101 | 25 customers | Total cost `7170.6752` | `0.37` | Capacity + time-window penalties | Solomon R-type instance |
| GA-VRPTW | C204 | 100 customers | Total cost `43059.6433` | `14.06` | Capacity + time-window penalties | Solomon C-type instance |

## Notes On Comparability

The numerical objective values are not directly comparable across all rows.

POMO-TSP reports route length for TSP instances. POMO-CVRP reports route length for generated CVRP instances. GA-VRPTW reports a cost value that includes fixed vehicle cost, travel cost, waiting cost, and delay cost. Therefore, the table should be read as a baseline recreation record rather than a strict ranking of methods.

## Observations

POMO-TSP shows the expected scale effect: moving from TSP20 to TSP100 increases both the route score and runtime. Augmentation slightly improves the score in both cases.

POMO-CVRP is more relevant to the EVRP-TW project than TSP because it includes vehicle capacity. However, it still has no time windows, battery state, or charging stations.

GA-VRPTW is useful because it already includes time-window-related behavior and Solomon benchmark instances. However, it does not include electric vehicle battery constraints or charging station decisions.

## Reflection

POMO and GA provide complementary baselines. POMO is a learning-based constructive policy: after training, it builds routes by selecting nodes step by step. GA is a search-based heuristic: it evolves customer permutations through selection, crossover, and mutation.

For the target EVRP-TW problem, neither baseline is complete. POMO needs time-window state, battery state, charging stations, and corresponding feasibility masks. GA needs at least an energy constraint and ideally charging-station insertion or repair logic.

The main insight from Week 2 is that EVRP-TW cannot be treated as just a longer routing problem. A useful baseline must report feasibility together with objective value, because a short route can still be invalid if it violates time windows or battery limits.

## Next Steps

- Use POMO-CVRP as the learning-based baseline reference for policy training structure.
- Use GA-VRPTW as the heuristic baseline reference for route representation and time-window penalties.
- Extend future experiments toward EVRP-TW by adding battery consumption, charging stations, and feasibility checks.
- Keep reporting objective value, runtime, feasibility status, and constraint violations together.
