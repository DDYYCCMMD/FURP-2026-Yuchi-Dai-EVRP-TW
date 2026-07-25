# Week 6: Full-Recharge ALNS for EVRPTW

This lab implements a minimum end-to-end Adaptive Large Neighborhood Search
(ALNS) solver for the Electric Vehicle Routing Problem with Time Windows
(EVRPTW).

The search framework is adapted from Keskin and Catay (2016), while the
problem model follows the full-recharge setting of Schneider, Stenger, and
Goeke (2014). Partial charging is intentionally excluded from Week 6.

## 1. Scope

Implemented:

- raw-unit Schneider instance loading;
- customer coverage, route structure, capacity, time-window, and battery
  evaluation;
- deterministic greedy initial construction;
- random, worst-distance, and related customer removal;
- greedy and regret-2 customer insertion;
- greedy charging-station insertion;
- relocate and intra-route 2-opt local search;
- segment-based adaptive operator weights;
- feasibility-first simulated annealing acceptance;
- reproducible instance/seed experiments;
- CSV result and JSON configuration output;
- a VRPTW ablation mode using the same customer data.

Not implemented:

- partial charging or departure-battery decision variables;
- nonlinear charging curves;
- station removal operators;
- simultaneous multi-station path search on one infeasible arc;
- heterogeneous vehicles;
- optimality guarantees;
- complete numerical reproduction of Keskin and Catay (2016).

This is therefore a method-level full-recharge adaptation, not a complete
reproduction of the EVRPTW-PR paper.

## 2. Directory Structure

```text
labs/week6/
├── README.md
├── Makefile
├── src/
│   ├── run_week6_alns.py
│   └── alns/
│       ├── config.py
│       ├── models.py
│       ├── instance_loader.py
│       ├── evaluator.py
│       ├── solution_utils.py
│       ├── construction.py
│       ├── charging_repair.py
│       ├── operators.py
│       ├── adaptive_weights.py
│       ├── acceptance.py
│       └── alns_solver.py
└── tests/
    ├── helpers.py
    ├── test_config.py
    ├── test_instance_loader.py
    ├── test_evaluator.py
    ├── test_charging_repair.py
    ├── test_acceptance.py
    ├── test_adaptive_weights.py
    └── test_alns_solver.py
```

The main project `src/` and the Week 5 GA implementation are not modified by
this lab.

## 3. Problem Representation

Each route explicitly begins and ends at the depot:

```text
[D0, C3, S1, C8, D0]
```

A complete solution is a list of vehicle routes:

```text
[
    [D0, C3, S1, C8, D0],
    [D0, C2, C5, D0],
]
```

Node types follow the Schneider files:

```text
d = depot
c = customer
f = charging station
```

The loader keeps all quantities in their original units:

```text
Q = battery capacity
C = vehicle load capacity
r = energy consumption per unit distance
g = charging time per unit energy
v = vehicle speed
```

This is deliberately separate from the normalized RL tensor loader under the
main project `src/data/`.

## 4. Unified Evaluator

For every edge `i -> j`, the evaluator applies:

```text
distance_ij       = EuclideanDistance(i, j)
travel_time_ij    = distance_ij / v
energy_used_ij    = r * distance_ij
battery_arrival_j = battery_departure_i - energy_used_ij
arrival_time_j    = departure_time_i + travel_time_ij
service_start_j   = max(arrival_time_j, ready_time_j)
```

At a customer:

```text
load += demand_j
departure_time = service_start_j + service_time_j
```

At a charging station:

```text
charge_amount = Q - battery_arrival_j
charging_time = g * charge_amount
battery_departure_j = Q
```

Battery is checked before recharge and is never clamped before the violation
is recorded.

The evaluator reports:

- total distance and travel time;
- waiting and charging time;
- vehicle and station-visit counts;
- capacity, time-window, and energy violations;
- late-customer count;
- minimum battery;
- missing and duplicated customers;
- route-structure violations;
- strict feasibility.

A candidate is feasible only if every customer is served exactly once and all
enabled hard constraints are satisfied.

## 5. Initial Construction

Customers are ordered by due time and inserted one at a time.

For each customer:

1. remove existing station visits temporarily;
2. test every insertion position in existing routes;
3. test opening a new route;
4. run charging-station repair when battery constraints are enabled;
5. reject capacity-, time-, or energy-infeasible candidates;
6. choose the candidate with the fewest vehicles and shortest distance.

This creates a deterministic feasible starting point before ALNS begins.

## 6. Charging-Station Repair

The Greedy Station Insertion procedure:

1. finds the first node reached with negative battery;
2. tries each station on the failing arc;
3. if necessary, tries progressively earlier arcs;
4. rejects unreachable stations and time-window-breaking insertions;
5. selects the feasible insertion with the smallest added distance;
6. repeats until the route is energy-feasible or the insertion budget is
   exhausted.

Every station insertion triggers complete route reevaluation because charging
time can make later customers infeasible.

## 7. ALNS Operators

Destroy operators:

- `random_removal`: removes a bounded random customer subset;
- `worst_removal`: removes customers with the largest direct distance saving;
- `related_removal`: removes customers close in space and time-window values.

Repair operators:

- `greedy_insertion`: selects the currently cheapest feasible insertion;
- `regret_2_insertion`: prioritizes customers with expensive alternatives.

Local search:

- `relocate`: removes and reinserts one customer;
- `2-opt`: reverses an intra-route customer subsequence.

Station visits are recalculated after customer-order changes. This avoids
preserving charging stops that are no longer necessary.

## 8. Adaptive Operator Weights

Destroy and repair operators have separate roulette-wheel weights.

At the end of each segment:

```text
new_weight
= (1 - reaction_factor) * old_weight
  + reaction_factor * average_segment_reward
```

Default rewards:

```text
new global best       = 5
improved current      = 3
SA-accepted worse     = 1
accepted neutral move = 0
rejected move         = 0
```

Equal-objective candidates remain accepted so the search can move across a
plateau, but they do not increase operator weights. The solver reports neutral
and SA-accepted-worse moves separately, so a high acceptance count is not
mistaken for frequent improvement.

Weights are bounded below by `minimum_weight`, so no operator disappears
permanently.

## 9. Simulated Annealing Acceptance

The implementation is feasibility-first:

```text
infeasible candidate              -> reject
fewer vehicles                    -> accept
more vehicles                     -> reject
same vehicles and shorter route   -> accept
same vehicles and equal distance  -> accept as neutral
same vehicles and longer route    -> accept with exp(-delta / temperature)
```

Therefore SA explores distance alternatives without trading away hard
feasibility or increasing the vehicle count.

## 10. Configuration

All defaults are centralized in:

```text
labs/week6/src/alns/config.py
```

Main groups:

- `EvaluatorConfig`: tolerance, full recharge, battery-ablation switch;
- `OperatorConfig`: removal sizes, local-search budgets, repair budget;
- `AdaptiveWeightConfig`: segment length, reaction factor, rewards;
- `SimulatedAnnealingConfig`: initial temperature and cooling;
- `ExperimentConfig`: instances, seeds, iterations, time limit, output path.

Benchmark parameters `Q/C/r/g/v` are never hard-coded in the algorithm
configuration; they are loaded from each instance.

## 11. Data

Default small instances:

```text
c101C5
r105C5
rc105C5
```

They provide clustered, random, and mixed customer structures. Instance files
are read from:

```text
data/schneider_instances/
```

The same code can run the 100-customer `_21` files, but the current operator
enumeration is designed first for correctness on small instances.

## 12. Running

Run commands from the repository root.

Validate configuration and data parsing:

```bash
python -m labs.week6.src.run_week6_alns --check-config
```

Run full-recharge EVRPTW:

```bash
python -m labs.week6.src.run_week6_alns --mode evrptw
```

Run the time-window/capacity ALNS ablation:

```bash
python -m labs.week6.src.run_week6_alns --mode vrptw
```

Run selected instances and seeds:

```bash
python -m labs.week6.src.run_week6_alns \
  --mode evrptw \
  --instances c101C5 r105C5 rc105C5 \
  --seeds 64 65 66 \
  --iterations 1000 \
  --time-limit 0 \
  --output-dir results/week6/main_fixed1000
```

Disable individual ALNS mechanisms:

```bash
python -m labs.week6.src.run_week6_alns --disable-sa
python -m labs.week6.src.run_week6_alns --disable-adaptive
```

The default is no wall-clock limit. Formal method comparisons should use the
same fixed iteration count and `--time-limit 0`; this prevents slow EVRPTW
instances from receiving fewer search iterations. A positive time limit is
still useful for smoke tests or a separate runtime-scalability experiment.

Equivalent Make targets:

```bash
make -C labs/week6 check-config
make -C labs/week6 run-evrptw
make -C labs/week6 run-vrptw
```

## 13. Outputs

Results are written to:

```text
results/week6/
```

Files:

```text
alns_evrptw_summary.csv
alns_evrptw_config.json
alns_vrptw_summary.csv
alns_vrptw_config.json
```

The CSV contains:

- instance, seed, and method;
- strict feasibility;
- vehicles, distance, and runtime;
- completed and best iteration;
- accepted, improving, neutral, and SA-accepted-worse move counts;
- termination reason and whether the wall-clock limit was hit;
- missing/duplicate/late customer and route-structure audit fields;
- capacity, time-window, and energy violations;
- minimum battery;
- station visits and charging time;
- final adaptive weights;
- complete best routes.

## 14. Intended Comparison

The Week 6 comparison is:

```text
GA + Week 5 repair
ALNS + time window / capacity
ALNS + time window / capacity / battery
```

The two ALNS modes use the same loader, customers, evaluator metrics, seeds,
and fixed iteration budget. The Week 5 GA is a battery-unaware historical
baseline and should be labeled as such.

Do not compare the old GA aggregate cost directly with ALNS distance. Report
common metrics such as feasibility, vehicles, distance, violations, and
runtime.

## 15. Analysis and Report

Generate the Week 6 report figures from the fixed formal CSV files:

```bash
python labs/week6/src/plot_week6_results.py
```

The script excludes old smoke and time-capped pilot results and writes eight
figures to:

```text
docs/figures/week06/
```

The complete analysis and interpretation are recorded in:

```text
docs/week06_alns_evrptw_report.md
```

The formula-driven analysis workbook and aggregate CSV tables are stored in:

```text
outputs/week6_analysis_20260725/
```

## 16. Tests

Tests have been written for:

- configuration validation;
- raw Schneider parsing;
- sufficient and insufficient battery;
- simultaneous time-window and energy violations;
- customer coverage;
- charging-station insertion;
- time-window rejection after charging;
- SA acceptance;
- adaptive weight updates;
- customer preservation in an end-to-end small solve.

When testing is enabled:

```bash
python -m pytest -q labs/week6/tests
```

## 17. References

- Schneider, Stenger, and Goeke (2014), *The Electric Vehicle-Routing
  Problem with Time Windows and Recharging Stations*:
  [`resource/papers/03_schneider2014_evrptw.pdf`](../../resource/papers/03_schneider2014_evrptw.pdf)
- Keskin and Catay (2016), *Partial Recharge Strategies for the Electric
  Vehicle Routing Problem with Time Windows*:
  [`resource/papers/04_keskincatay2016_partial_recharge.pdf`](../../resource/papers/04_keskincatay2016_partial_recharge.pdf)
