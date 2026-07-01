# Week 3 GA-VRPTW Experiment Report

This report addresses the Week 3 lab task in [`labs/tasks/week03_works.md`](../labs/tasks/week03_works.md). The aim of this week was not only to reproduce a baseline, but to evaluate it under a controlled comparison and explain what the results do and do not show.

## Experiment Question

The experiment question is:

Can a larger GA search budget improve the solution quality of the GA-VRPTW baseline on Solomon VRPTW instances, and is the improvement large enough to justify the extra runtime?

More specifically, the comparison tests whether increasing population size and generation count leads to consistently lower penalized routing cost across different instance types and customer scales.

## Solver And Comparison Design

The tested solver is the cloned GA-VRPTW baseline in [`labs/week3/py-ga-VRPTW`](../labs/week3/py-ga-VRPTW), executed through the reusable experiment entrypoint [`labs/week3/py-ga-VRPTW/run_experiment.py`](../labs/week3/py-ga-VRPTW/run_experiment.py).

Two search-budget configurations were compared:

| Config | Population Size | Generations | Purpose |
|---|---:|---:|---|
| Default | 80 | 100 | Reference budget |
| High-Budget | 160 | 200 | Larger search effort |

Other parameters were fixed to keep the comparison fair:

- `unit_cost=8.0`
- `init_cost=60.0`
- `wait_cost=0.5`
- `delay_cost=1.5`
- `cx_pb=0.85`
- `mut_pb=0.01`

This means the main controlled variable is search budget, not the problem definition or cost structure.

## Experimental Setup

### Instances And Scales

The experiment used three Solomon instance families:

- `R101`: random customer distribution
- `C101`: clustered customer distribution
- `RC101`: mixed random-clustered distribution

Two customer scales were tested:

- `ind_size=25`
- `ind_size=50`

Each setting was repeated with three random seeds:

- `11`
- `22`
- `33`

Total experiment count:

- `3` instance families
- `2` scales
- `2` configurations
- `3` seeds
- Total = `36` runs

### Runtime Environment

The experiments were executed locally on:

- macOS `26.3`
- architecture: `arm64` (Apple Silicon)
- Python `3.11.15`
- Conda environment: `evrptw`

### Recorded Outputs

For each run, the following information was retained:

- instance name
- customer scale
- configuration
- random seed
- final `Total cost`
- runtime in seconds
- generation-level CSV log
- full terminal log

The cleaned run-level table is stored in [`labs/week3/ga_vrptw_week3_results.csv`](../labs/week3/ga_vrptw_week3_results.csv).

Generation-level CSV files are stored in [`labs/week3/py-ga-VRPTW/results`](../labs/week3/py-ga-VRPTW/results), and run logs are stored in [`labs/week3/py-ga-VRPTW/experiment_logs`](../labs/week3/py-ga-VRPTW/experiment_logs).

## Constraint Handling And Feasibility Interpretation

This section is important for interpreting the results correctly.

In the current GA implementation, route splitting in [`labs/week3/py-ga-VRPTW/gavrptw/core.py`](../labs/week3/py-ga-VRPTW/gavrptw/core.py) treats some constraints more strictly than others:

- In `ind2route()`, vehicle capacity and a route-level return-time bound are checked when deciding whether a customer can stay in the current sub-route.
- In `eval_vrptw()`, customer time windows are not enforced as a hard accept/reject constraint. Instead, early arrival creates waiting cost and late arrival creates delay penalty.

Therefore, the final `Total cost` should be interpreted as a **penalized objective**, not as a direct certificate of strict hard-feasible time-window satisfaction.

This matters because:

- a lower cost means the solver found a better trade-off under the chosen penalty model;
- a higher cost may reflect more travel distance, more waiting, more lateness, or a combination of these;
- the current implementation does not output an explicit feasible/infeasible flag for customer-level time-window satisfaction.

As a result, this report does **not** claim a strict feasible-rate comparison. Instead, it evaluates:

- penalized solution quality;
- runtime;
- seed-to-seed stability.

This interpretation is more honest and better aligned with what the code actually computes.

## Aggregated Results

| Instance | Size | Config | Avg. Cost | Best Cost | Cost Std. | Avg. Runtime (s) |
|---|---:|---|---:|---:|---:|---:|
| R101 | 25 | Default | 7894.61 | 7535.34 | 580.99 | 0.2387 |
| R101 | 25 | High-Budget | 7218.12 | 6968.12 | 226.86 | 1.1607 |
| R101 | 50 | Default | 17479.79 | 16740.01 | 651.80 | 0.3961 |
| R101 | 50 | High-Budget | 16555.32 | 15230.55 | 1148.34 | 1.7818 |
| C101 | 25 | Default | 9734.75 | 9051.81 | 855.32 | 0.2314 |
| C101 | 25 | High-Budget | 8424.75 | 7956.17 | 419.10 | 1.1227 |
| C101 | 50 | Default | 26178.15 | 25389.90 | 789.17 | 0.3859 |
| C101 | 50 | High-Budget | 24486.74 | 23563.33 | 979.85 | 1.7701 |
| RC101 | 25 | Default | 7676.24 | 6327.90 | 1173.70 | 0.2401 |
| RC101 | 25 | High-Budget | 6663.85 | 6056.34 | 569.70 | 1.1535 |
| RC101 | 50 | Default | 22906.22 | 21821.52 | 954.31 | 0.4032 |
| RC101 | 50 | High-Budget | 21910.39 | 21237.09 | 721.36 | 1.8070 |

## Budget Trade-Off Summary

The table below highlights the direct comparison between the two configurations for each instance-scale pair.

| Instance | Size | Avg. Cost Improvement | Relative Improvement | Runtime Multiplier |
|---|---:|---:|---:|---:|
| R101 | 25 | 676.49 | 8.57% | 4.86x |
| R101 | 50 | 924.48 | 5.29% | 4.50x |
| C101 | 25 | 1310.00 | 13.46% | 4.85x |
| C101 | 50 | 1691.41 | 6.46% | 4.59x |
| RC101 | 25 | 1012.38 | 13.19% | 4.80x |
| RC101 | 50 | 995.82 | 4.35% | 4.48x |

## Main Findings

### 1. Higher budget improved average cost in every comparison

The High-Budget setting outperformed the Default setting on all six instance-scale combinations. This is the clearest finding of the experiment. The effect was not isolated to one family or one seed.

### 2. The strongest gains appeared on 25-customer settings

The relative gains were largest on:

- `C101-25`: `13.46%`
- `RC101-25`: `13.19%`

This suggests that on smaller instances, extra search effort can convert more directly into better penalized routing cost.

### 3. Runtime increased by about five times

The High-Budget setting required about `4.5x` to `4.9x` the runtime of the Default setting. Therefore, the quality improvement is real, but it is not free.

### 4. Stability improved in some cases, but not all

The cost standard deviation decreased for:

- `R101-25`
- `C101-25`
- `RC101-25`
- `RC101-50`

This suggests more consistent outcomes across seeds in those settings.

However, standard deviation increased for:

- `R101-50`
- `C101-50`

So a larger budget does not automatically guarantee more stable behavior on larger problems.

## Discussion

The results support a practical interpretation rather than an absolute one.

If the goal is to obtain lower penalized routing cost and runtime is not a major constraint, then the High-Budget setting is preferable. It produced better average results in every tested case and often reduced seed sensitivity on smaller instances.

If the goal is fast iteration, parameter tuning, or repeated exploratory runs, then the Default setting remains attractive because it is much faster and still produces reasonable results. For this reason, the Default setting is a good development configuration, while the High-Budget setting is better suited for final evaluation.

Instance structure also seems to matter. The clustered and mixed instances (`C101`, `RC101`) showed especially clear gains at the 25-customer scale, while the 50-customer settings still improved but with smaller relative benefits. This may indicate that the larger search budget is increasingly consumed by combinatorial growth as the problem becomes larger.

## Why This Satisfies Week 3

This work satisfies the main goals of Week 3 for several reasons:

- it defines a clear experiment question rather than only running provided samples;
- it compares methods fairly by changing only the search budget while keeping the underlying solver and cost model fixed;
- it evaluates more than one scale;
- it uses repeated trials for a stochastic method;
- it reports both quality and runtime;
- it discusses what can and cannot be concluded from the metric.

In other words, the task moved from baseline recreation to evidence-based evaluation.

## Limitations

- This is still a VRPTW baseline, not a full EVRP-TW solver.
- The reported `Total cost` is a penalized objective, not a strict hard-feasibility proof for all customer time windows.
- The experiment did not separately log lateness counts or total lateness magnitude, so time-window violations cannot yet be decomposed from the overall cost.
- Only 3 seeds were used per setting. This is acceptable for a Week 3 lab study, but still limited for stronger statistical claims.
- Only one instance from each family was used. Broader coverage across more Solomon instances would make the conclusion stronger.

## Conclusion

This Week 3 experiment shows that increasing GA search budget improves penalized solution quality consistently across all tested Solomon instance-scale settings, but the improvement comes at roughly five times the runtime. The best relative gains appeared on the 25-customer `C101` and `RC101` settings, while larger 50-customer cases showed smaller but still positive improvements. The most important interpretation point is that these results compare **penalized VRPTW solution quality**, not strict hard-feasible EVRP-TW performance. A strong next step would be to keep this GA as a heuristic baseline and extend the evaluation with explicit lateness statistics, battery-related constraints, or a simple EV-specific penalty design.
