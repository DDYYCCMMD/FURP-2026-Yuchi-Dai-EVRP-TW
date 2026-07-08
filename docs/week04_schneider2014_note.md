# Week 4 Reading Note — Schneider, Stenger & Goeke (2014)

**Paper:** Michael Schneider, Andreas Stenger, and Dominik Goeke. 2014. *The Electric Vehicle-Routing Problem with Time Windows and Recharging Stations*. Transportation Science, 48(4), 500-520. DOI: 10.1287/trsc.2013.0490.

## Why This Paper Matters

This paper is the canonical source for the Electric Vehicle Routing Problem with Time Windows and Recharging Stations, usually written as E-VRPTW or EVRP-TW. It extends the classical VRPTW by adding two electric-vehicle-specific elements:

- limited battery capacity;
- visits to recharging stations during a route.

This makes the problem much harder than VRPTW. A route can be short and still invalid if the vehicle runs out of battery before reaching a customer, a charging station, or the depot. Charging also consumes time, so energy decisions interact directly with customer time windows.

For this project, Schneider et al. is important because Lin et al. (2021), the target DRL paper, builds on this problem setting and benchmark family.

## Problem Setting

The problem is defined on a directed graph containing customers, charging stations, and two depot copies:

- `V = {1, ..., N}`: customer set;
- `F`: original charging station set;
- `F'`: dummy copies of charging stations, used to allow multiple visits to the same physical station;
- `0`: start depot;
- `N + 1`: end depot.

The start depot `0` and end depot `N + 1` represent the same physical depot, but they are separated in the mathematical model so that each route has a clean structure:

```text
0 -> customer/station -> ... -> customer/station -> N+1
```

Common set notation in the paper:

```text
V'          = customers + dummy charging station nodes
V'_0        = V' + start depot
V'_{N+1}    = V' + end depot
V'_{0,N+1}  = V' + start depot + end depot
```

The binary routing variable is:

```text
x_ij = 1 if arc i -> j is travelled
x_ij = 0 otherwise
```

This is the main route-choice decision variable. For example, if a route is:

```text
0 -> 3 -> 5 -> N+1
```

then:

```text
x_0,3 = 1
x_3,5 = 1
x_5,N+1 = 1
```

and all other unused arcs have value `0`.

## Main Constraints

The E-VRPTW includes several types of constraints:

| Constraint | Meaning |
|---|---|
| Customer service | Every customer must be served exactly once. |
| Flow conservation | If a vehicle enters a customer or station node, it must also leave it. |
| Depot structure | Routes start at `0` and end at `N + 1`. |
| Vehicle capacity | Total customer demand on a route cannot exceed vehicle capacity. |
| Time windows | Service at customer `i` must start within `[e_i, l_i]`. |
| Battery capacity | Battery level cannot become negative and cannot exceed capacity. |
| Recharging | At charging stations, the vehicle can recharge before continuing. |

The time constraints are easiest to understand as route simulation. If a vehicle travels from node `i` to node `j`, then the arrival or service start time at `j` must be after the time spent at `i` plus travel time.

For a normal customer node:

```text
T_j >= T_i + service_time_i + travel_time_ij
```

For a charging station:

```text
T_j >= T_i + charging_time_i + travel_time_ij
```

In Schneider et al., charging time depends on the battery level when reaching the station:

```text
charging_time = g * (Q - y_i)
```

where:

- `Q` is battery capacity;
- `y_i` is remaining battery when arriving at station `i`;
- `g` is charging time per unit of energy.

The paper assumes full recharge at charging stations. This is different from later partial-recharge papers, where the amount of charged energy becomes another decision.

## Feasibility And Violations

A feasible E-VRPTW solution must satisfy all hard constraints. An infeasible solution may still contain a route, but it violates at least one constraint.

Important violation types:

| Violation | Example |
|---|---|
| Customer violation | A customer is missed or served twice. |
| Capacity violation | A route carries more demand than vehicle capacity. |
| Time-window violation | Vehicle arrives later than the customer's latest service time. |
| Battery violation | Vehicle does not have enough energy to reach the next node. |
| Depot violation | A route does not start/end at the depot correctly. |

This distinction is important for the current GA baseline in this repository. The Week 3 GA solver is a VRPTW solver, not a full EVRP-TW solver. It handles time windows mainly through delay penalties, so a lower `Total cost` does not automatically prove strict feasibility.

For Week 4, this suggests a useful improvement: add explicit violation statistics, such as:

- number of late customers;
- total lateness;
- maximum lateness;
- capacity violation flag;
- number of routes;
- later, battery or energy violation.

## Solution Method: VNS/TS Hybrid

Schneider et al. propose a hybrid metaheuristic combining:

- Variable Neighborhood Search (VNS);
- Tabu Search (TS);
- Simulated Annealing style acceptance of worse solutions;
- adaptive penalty mechanisms.

### Variable Neighborhood Search

VNS changes the type of local search move when the current neighborhood cannot improve the solution. Typical route neighborhoods include:

- relocate a customer;
- swap two customers;
- reverse a route segment;
- move customers between routes;
- insert or remove charging station visits.

The reason VNS is useful is that one move type may get stuck in a local optimum, while another move type may still find an improvement.

### Translocation Chain

A translocation chain is a chain of relocate operations. Moving one customer to another position may force another customer to move, which may then force another move. This can repair or improve routes more flexibly than moving a single customer once.

In EVRP-TW, this is useful because one local change can affect capacity, time windows, and battery feasibility at the same time.

### Tabu Search

Tabu Search prevents the search from undoing a recent move immediately. For example, if customer `5` is moved from route A to route B, the reverse move can be forbidden for several iterations.

This helps avoid cycling:

```text
A -> B -> A -> B -> ...
```

The tabu tenure controls how long a move remains forbidden.

### Simulated Annealing Deterioration

The SA deterioration percentage controls how much worse a candidate solution may be accepted during search. This is useful because accepting a slightly worse solution can help escape local optima.

Example:

```text
current cost = 1000
allowed deterioration = 5%
candidate cost up to about 1050 may still be accepted
```

This does not mean the final solution should be worse. It is a temporary exploration mechanism.

## Penalty Parameters

The paper tunes several algorithm parameters, including:

- SA deterioration percentage;
- initial penalties such as `alpha_0`, `beta_0`, `gamma_0`;
- penalty lower and upper limits;
- penalty update factor;
- number of penalty update iterations;
- minimum and maximum tabu tenure;
- diversification penalty;
- number of Tabu Search iterations.

These are not problem-definition variables. They are algorithm-control parameters. Their purpose is to manage the search process, especially when the heuristic temporarily allows infeasible solutions.

A simplified penalty objective can be understood as:

```text
penalized cost
= route cost
+ alpha * capacity violation
+ beta  * time-window violation
+ gamma * battery violation
```

If the search produces too many infeasible solutions, penalties can be increased. If the search becomes too conservative, penalties can be decreased.

## Key Takeaways

1. EVRP-TW is not just VRPTW with more nodes. Battery state and charging time make route feasibility path-dependent.

2. Charging stations must be part of the route decision. A route may need a detour to a station to remain feasible, even if that detour increases distance.

3. Full recharge is assumed in Schneider et al. This simplifies the model compared with partial recharge, because the charging decision is mainly whether and where to recharge, not how much to recharge.

4. Feasibility should be reported explicitly. Objective value alone is not enough, because a low-cost solution may violate time windows or battery constraints.

5. The VNS/TS method gives several ideas for improving the current GA baseline: local search, repair moves, adaptive penalties, and explicit violation metrics.

## Connection To Week 4 Work

The current GA baseline in `labs/week3/py-ga-VRPTW` solves a VRPTW-style problem. It includes capacity and time-window penalties but does not model electric vehicle battery or charging stations.

For Week 4, Schneider et al. suggests two realistic extension directions:

### Direction 1: Add Explicit Violation Evaluation

Before adding battery logic, improve the experiment reporting by separating:

- transport cost;
- waiting time;
- delay penalty;
- late customer count;
- total lateness;
- maximum lateness.

This would make the GA results more interpretable and align the report with the feasibility emphasis in EVRP-TW literature.

### Direction 2: Add A Simple Energy-Aware Proxy

A small EV-related extension could add a route-level battery proxy:

```text
if route_distance > battery_capacity:
    add battery penalty
```

This is not a full EVRP-TW model because it does not insert charging station visits, but it would be a first step toward energy-aware routing.

### Recommended Week 4 Choice

The safest Week 4 experiment is:

```text
time-window violation metrics + delay penalty sensitivity
```

This is directly connected to the current GA code and can produce a clear report. A possible experiment is to compare:

```text
delay_cost = 1.5
delay_cost = 5.0
delay_cost = 10.0
```

and evaluate whether stronger lateness penalties reduce time-window violations, at what cost in total objective and runtime.

## Useful Sentences For Report

Schneider et al. (2014) defines the canonical E-VRPTW by extending VRPTW with limited battery capacity and recharging station visits. The paper shows that route feasibility depends not only on customer order and vehicle capacity, but also on the remaining battery and the time consumed by recharging. This motivates reporting explicit feasibility and violation metrics rather than only objective value.

The current GA baseline used in this project is still a VRPTW heuristic, so it cannot yet reproduce the full Schneider E-VRPTW setting. However, Schneider et al.'s penalty-based and neighborhood-search ideas provide a practical direction for Week 4: first separate time-window violations from the aggregate penalized cost, then test whether stronger delay penalties improve feasibility.

