# EVRP-TW Reference Handbook

> Quick-reference document — consolidates problem variables, core metrics, benchmarks, SOTA tools, and key concepts for the EVRP-TW Deep RL project.
> Sources: VRP-EVRP-Project-Hub (Dr. Cui's Group), domain literature, personal annotations.

---

## Table of Contents

1. [Problem Variables and Notation](#1-problem-variables-and-notation)
2. [Problem Variant Hierarchy](#2-problem-variant-hierarchy)
3. [Core Evaluation Metrics](#3-core-evaluation-metrics)
4. [Minimum Reporting Standard](#4-minimum-reporting-standard)
5. [Failure Case Analysis Template](#5-failure-case-analysis-template)
6. [Benchmark Datasets](#6-benchmark-datasets)
7. [Recommended Baseline Ladder](#7-recommended-baseline-ladder)
8. [Tools and Codebases](#8-tools-and-codebases)
9. [SOTA Methods Overview](#9-sota-methods-overview)
10. [DRL Routing Architecture Notes](#10-drl-routing-architecture-notes)
11. [Search Keywords](#11-search-keywords)

---

## 1. Problem Variables and Notation

### Graph Structure

| Symbol | Meaning | Notes |
|---|---|---|
| $G = (V, A)$ | Routing graph | $V$ = node set, $A$ = directed arc set |
| $V = \{0\} \cup C \cup F$ | Node set | $0$ = depot, $C$ = customer set, $F$ = charging station set |
| $d_{ij}$ | Travel distance on arc $(i,j)$ | Typically Euclidean |
| $t_{ij}$ | Travel time on arc $(i,j)$ | Often $d_{ij}/v$ where $v$ = vehicle speed |

### Customer Nodes

| Symbol | Meaning | Notes |
|---|---|---|
| $q_i$ | Demand at customer $i$ | Weight or volume of goods |
| $[e_i,\ l_i]$ | Time window at customer $i$ | $e_i$ = earliest service time, $l_i$ = latest service time |
| $s_i$ | Service time at customer $i$ | Time spent loading/unloading |

### Vehicle Parameters

| Symbol | Meaning | Notes |
|---|---|---|
| $Q$ | Vehicle load capacity | |
| $B$ | Maximum battery capacity (kWh or normalised) | EVRP-TW specific |
| $h$ | Energy consumption rate per unit distance | Battery drain rate |
| $g$ | Charging rate | Battery gained per unit time at a station |
| $K$ | Fleet size (number of vehicles) | Upper bound |

### Decision Variables

| Symbol | Meaning |
|---|---|
| $x_{ijk} \in \{0,1\}$ | 1 if vehicle $k$ traverses arc $(i,j)$ |
| $\tau_{ik}$ | Arrival time of vehicle $k$ at node $i$ |
| $b_{ik}$ | Remaining battery of vehicle $k$ upon arrival at node $i$ |
| $u_{fk}$ | Charging duration of vehicle $k$ at station $f$ |

### Objective Function

$$\min \sum_k \sum_{(i,j)} d_{ij} \cdot x_{ijk} \quad \text{(minimise total travel distance)}$$

Sometimes multi-objective: minimise fleet size and total distance jointly.

### Key Constraints

| Constraint | Form | Description |
|---|---|---|
| Capacity | $\sum_{i \in C} q_i \cdot x_{ijk} \leq Q$ | Load must not exceed capacity |
| Time window | $e_i \leq \tau_{ik} \leq l_i$ | Arrival must be within the window |
| Battery (travel) | $b_{ik} - h \cdot d_{ij} \geq 0$ | Battery cannot go negative during travel |
| Battery (charge) | $b_{ik}' = b_{ik} + g \cdot u_{fk} \leq B$ | Cannot charge beyond maximum |
| Flow conservation | $\sum_j x_{ijk} = \sum_j x_{jik}$ | Vehicles enter and leave each node once |

---

## 2. Problem Variant Hierarchy

```
TSP (Travelling Salesman Problem)
 └─ VRP (Vehicle Routing Problem) — multiple vehicles + capacity
     └─ CVRP (Capacitated VRP)
         └─ VRPTW (+ time windows)
             └─ EVRP-TW (+ battery + charging stations)
                 └─ EVRP-TW with Partial Recharge (+ partial charging allowed)
                     └─ Ground-Air Collaborative EVRP-TW (+ truck-drone synchronisation)
```

| Variant | Additional Constraints | Notes |
|---|---|---|
| TSP | — | Single vehicle, no capacity |
| VRP | Multiple vehicles | |
| CVRP | Load capacity $Q$ | |
| VRPTW | Time windows $[e_i, l_i]$ | |
| EVRP | Battery $B$, charging stations $F$ | |
| EVRP-TW | Battery + time windows | **This project's core problem** |
| EVRP-TW (partial) | Partial recharge allowed | Vehicle need not charge to full |
| Truck-Drone VRP | Ground-air coordination, synchronisation constraints | |

> **Note:** Lin et al. (2021) assumes **full recharge** (always charges battery to $B$). Keskin & Çatay (2016) introduce partial recharge as an extension.

---

## 3. Core Evaluation Metrics

### Universal Metrics (required for all variants)

| Metric | Notes |
|---|---|
| Total distance / cost | Primary objective. **Never report this alone.** |
| Feasibility rate | Fraction of test instances yielding a feasible solution. Must be reported alongside objective value. |
| Runtime | In seconds; always state hardware. |
| Number of vehicles used | Sometimes a co-objective. |

### VRPTW / EVRP-TW Specific

| Metric | Notes |
|---|---|
| Time-window violations (count) | Number of customers arrived after $l_i$ |
| Time-window violation magnitude | Total lateness $\sum \max(0,\ \tau_i - l_i)$ |
| Capacity violations | Number of routes or total excess load |
| Energy violations | Number of arcs where battery would go negative |
| Charging count | Number of charging station visits per route |
| Charging time | Total time spent waiting at charging stations |
| Minimum residual battery | Lowest battery level recorded across all routes; higher = safer |

### Truck-Drone Collaboration Specific

| Metric | Notes |
|---|---|
| Makespan | Time at which the last vehicle / drone completes its mission |
| Synchronisation violations | Number of missed drone recovery events |

### The Golden Rule for Reporting

> ❌ "Total distance = 42.3" — **not acceptable**
>
> ✅ "Total distance 42.3 | feasibility rate 100% | TW violations 0 | charging visits 2 | runtime 0.3 s (MacBook Pro M3)" — **correct**

---

## 4. Minimum Reporting Standard

Every experimental result must include:

1. Results on **at least 3 instance sizes or 3 representative instances** (baseline vs. improved method).
2. Objective value **and** feasibility status together — neither alone is sufficient.
3. Runtime and hardware specification.
4. Random seeds and solver/model parameters.
5. **At least 3 failure cases** with constraint-level diagnosis.

---

## 5. Failure Case Analysis Template

For each failed or poor-quality route, record:

```
Instance name and size:
Solver / model used:
Objective value:
Feasibility status:
Constraints violated:
Step at which the route first becomes infeasible:
Possible fix or next experiment:
```

Common failure modes:

| Cause | Symptom | Mitigation |
|---|---|---|
| Time windows too tight | Many customers arrived after $l_i$ | Relax instance parameters; add waiting-time handling |
| Insufficient battery | Battery goes negative between stations | Increase charging frequency; reduce instance scale |
| Capacity overload | Route demand exceeds $Q$ | Add vehicles; redistribute customers |
| Greedy policy | DRL minimises distance but ignores feasibility | Strengthen masking; penalise constraint violations |

---

## 6. Benchmark Datasets

### Solomon VRPTW Instances (1987)

- **Sizes:** 25 / 50 / 100 customers
- **Instance types:**
  - C1, C2 — clustered customers; C2 has wider time windows
  - R1, R2 — randomly distributed; R2 has wider time windows
  - RC1, RC2 — mixed distribution
- **Source:** [vrptw.org](http://www.vrptw.org/) or paper appendix
- **Use:** Standard VRPTW benchmark; virtually all routing papers report results here

### Schneider EVRP-TW Instances (2014)

- **Structure:** Extended from Solomon instances with charging station nodes inserted into the network
- **Charging setup:** Each instance contains $|F|$ charging station nodes
- **Battery parameters:** Normalised; typically $B = 1.0$, energy consumption linear in distance
- **Source:** [Schneider et al. (2014)](https://doi.org/10.1287/trsc.2013.0490) appendix
- **Use:** Standard EVRP-TW benchmark; used by Lin et al. (2021)

### Instance Naming Convention (Schneider)

```
c101_21.txt  →  c: cluster type | 101: Solomon base instance | 21: number of charging stations added
```

---

## 7. Recommended Baseline Ladder

Follow in order — **do not skip steps:**

```
Step 1 — CVRP          with OR-Tools or PyVRP
Step 2 — VRPTW         add time windows; report TW violations
Step 3 — EVRP-TW       add battery constraints; report energy violations + charging count
Step 4 — Neural baseline  POMO on CVRP; understand RL training pipeline
Step 5 — Extension     hybrid method, partial recharge, or truck-drone collaboration
```

> If Step 2 does not run cleanly, Step 5 is meaningless.

---

## 8. Tools and Codebases

| Tool | Purpose | Link |
|---|---|---|
| **OR-Tools** | Exact / heuristic CVRP and VRPTW | [developers.google.com/optimization/routing](https://developers.google.com/optimization/routing) |
| **PyVRP** | High-quality heuristic VRP baseline (Python) | [github.com/PyVRP/PyVRP](https://github.com/PyVRP/PyVRP) |
| **RL4CO** | DRL routing experiment framework (AM, POMO, and more) | [github.com/ai4co/rl4co](https://github.com/ai4co/rl4co) |
| **POMO** | Strong RL baseline with symmetric augmentation | [github.com/yd-kwon/POMO](https://github.com/yd-kwon/POMO) |
| **Attention-Learn-to-Route** | Kool 2019 official code | [github.com/wouterkool/attention-learn-to-route](https://github.com/wouterkool/attention-learn-to-route) |
| **HGS-CVRP** | Strong classical CVRP baseline (C++) | [github.com/vidalt/HGS-CVRP](https://github.com/vidalt/HGS-CVRP) |
| **VRPLIB** | VRP instance library | [vrp.atd-lab.inf.puc-rio.br](http://vrp.atd-lab.inf.puc-rio.br/) |

---

## 9. SOTA Methods Overview

### Classical Methods

| Method | Type | Reference |
|---|---|---|
| Clarke-Wright Savings | Construction heuristic | Clarke & Wright (1964) |
| LKH-3 | Local search | Helsgott et al. |
| HGS | Hybrid genetic search | Vidal et al. (2022) |
| Branch-and-Price | Exact solver | Desrochers et al. (1992) |

### Neural Combinatorial Optimization Methods

| Method | Year | Core Idea | Key Contribution |
|---|---|---|---|
| Pointer Networks | 2015 | Attention-based seq2seq node selection | First attention mechanism for routing |
| Neural CO (Bello et al.) | 2016 | RL training of Pointer Net on TSP | REINFORCE replaces supervised learning |
| Nazari et al. | 2018 | Element-wise embeddings + RL for VRP | Removes LSTM; extends to multi-vehicle |
| Attention Model (Kool et al.) | 2019 | Multi-head attention encoder + rollout baseline | State-of-the-art on TSP/VRP at publication |
| POMO | 2020 | $N$-start symmetric augmentation at inference | Large inference-time quality improvement |
| Lin et al. EVRP-TW | 2021 | AM extended to EVRP-TW with battery masking | **Target replication paper** |
| RL4CO | 2024 | Unified RL routing benchmark framework | Multi-model; easy to extend |
| CB-DRL | 2026 | Three-phase curriculum training for EVRP-TW | Resolves DRL training instability on dense constraints |

---

## 10. DRL Routing Architecture Notes

### Attention Model Backbone (Kool 2019)

```
Node features (coordinates, demand, time window, ...)
        ↓
Multi-head Attention Encoder  — learns graph structure representations
        ↓
Context Embedding  — encodes current vehicle state (position, load, time, battery)
        ↓
Single-head Attention Decoder  — computes compatibility score for each candidate node
        ↓
Softmax  →  selection probability distribution over nodes
        ↓
REINFORCE + Rollout Baseline  — policy gradient training
```

### Lin et al. (2021) Extensions on Top of AM

1. **Node-type differentiation** — depot, customers, and charging stations encoded with distinct feature vectors
2. **Battery mask** — a customer is masked if visiting it would leave insufficient battery to reach any charging station or the depot
3. **Time-window mask** — a node is masked if the earliest possible arrival already exceeds $l_i$
4. **Extended context vector** — current battery level $b$ and current time $\tau$ added to the decoder context embedding

### Reference Training Hyperparameters (Lin et al.)

| Hyperparameter | Reference Value |
|---|---|
| Hidden dimension | 128 |
| Attention heads | 8 |
| Encoder layers | 3 |
| Batch size | 512 |
| Learning rate | 1e-4 |
| Training instances per epoch | 128k |
| Rollout baseline update | Once per epoch |

### Feasibility vs. Short Routes

> A **short but infeasible** route is worse than a **slightly longer but feasible** route.
>
> Never report an infeasible solution as a good result.

---

## 11. Search Keywords

```
Electric Vehicle Routing Problem with Time Windows
EVRP-TW recharging stations
POMO CVRP reinforcement learning
neural combinatorial optimization vehicle routing
attention model vehicle routing
deep reinforcement learning EVRPTW
PyVRP vehicle routing Python
truck drone routing synchronization
Flying Sidekick Traveling Salesman Problem
curriculum learning vehicle routing
```

---

*Last updated: 2026-06-17*
*Sources: VRP-EVRP-Project-Hub (Dr. Cui's Group), Lin et al. (2021), Kool et al. (2019), Schneider et al. (2014), personal annotations*
