# Week 4 Reading Note — Keskin & Catay (2016)

**Paper:** Merve Keskin and Bulent Catay. 2016. *Partial Recharge Strategies for the Electric Vehicle Routing Problem with Time Windows*. Transportation Research Part C, 65, 111-127. DOI: 10.1016/j.trc.2016.01.013.

## Why This Paper Matters

This paper extends the EVRPTW setting of Schneider et al. (2014). Schneider assumes that whenever an electric vehicle visits a charging station, it recharges to full battery capacity. Keskin and Catay relax this assumption and allow partial recharge.

This is important because full recharge is often unnecessary. If a vehicle only needs enough energy to reach the next station or return to the depot, charging to 100% may waste time and cause time-window violations. Partial recharge can reduce charging duration and make tighter schedules feasible.

For this project, the paper is useful because it shows a realistic next step beyond the baseline EVRP-TW formulation:

```text
VRPTW -> EVRPTW with full recharge -> EVRPTW with partial recharge
```

## Problem Setting

The paper studies EVRPTW with Partial Recharges, written as EVRPTW-PR.

The basic constraints are inherited from EVRPTW:

- customers have demands, service times, and time windows;
- vehicles have limited freight capacity;
- vehicles have limited battery capacity;
- battery decreases with travelled distance;
- vehicles may visit charging stations during their routes;
- charging consumes time.

The main difference is the charging rule.

### Full Recharge

In Schneider et al. (2014), if a vehicle arrives at a charging station with battery level `y_i`, it charges to full capacity `Q`:

```text
recharged amount = Q - y_i
departure battery = Q
```

This means the charging amount is not a separate decision. Once the route visits a station, the vehicle must wait long enough to become full.

### Partial Recharge

In Keskin and Catay (2016), the vehicle may leave a station with any feasible battery level:

```text
y_i <= Y_i <= Q
```

where:

- `y_i` is the battery state when arriving at station `i`;
- `Y_i` is the battery state when departing from station `i`;
- `Q` is the maximum battery capacity.

The charged amount is:

```text
Y_i - y_i
```

The charging time is proportional to the charged amount:

```text
charging_time = g * (Y_i - y_i)
```

So the route decision now includes not only:

```text
which station to visit
```

but also:

```text
how much to charge there
```

This makes the problem more realistic, but also harder because recharge quantity becomes a continuous decision.

## Key Intuition

Partial recharge can improve routing decisions because charging too much may consume time that is more valuable than extra battery.

Example:

```text
current battery = 20
full battery Q = 100
energy needed to finish route = 40
```

Under full recharge:

```text
charge 80 units
```

Under partial recharge:

```text
charge only 40 units
```

The second option saves charging time. This saved time may allow the vehicle to satisfy a customer time window that would otherwise be missed.

The paper's core insight is that energy feasibility and time-window feasibility are coupled. More charging improves battery feasibility, but can hurt time-window feasibility.

## Mathematical Model Changes

The model follows Schneider et al.'s notation:

- `V`: customers;
- `F`: charging stations;
- `F'`: dummy station copies, allowing multiple visits;
- `0`: start depot;
- `N + 1`: end depot;
- `x_ij`: binary variable, equals 1 if arc `i -> j` is travelled.

The important new variable is:

```text
Y_i = battery state when leaving charging station i
```

In the full recharge model:

```text
Y_i = Q
```

In the partial recharge model:

```text
y_i <= Y_i <= Q
```

This is the main modeling contribution: charging is no longer fixed by the station visit itself.

## Solution Method: ALNS

The paper proposes an Adaptive Large Neighborhood Search, or ALNS.

ALNS is a destroy-and-repair heuristic:

```text
1. Start from a feasible solution.
2. Destroy part of it by removing customers and/or charging stations.
3. Repair it by reinserting customers and stations.
4. Accept or reject the new solution.
5. Adaptively learn which removal/insertion operators work well.
```

The "adaptive" part means the algorithm gives higher selection probability to operators that performed well in previous iterations.

This is different from a fixed local search. Instead of always applying the same move, ALNS maintains a set of possible removal and insertion mechanisms and learns which are useful during the run.

## Removal Operators

The paper uses several customer removal ideas:

- random customer removal;
- worst-distance customer removal;
- related/Shaw-style removal;
- route removal.

It also introduces EV-specific station-related removal mechanisms.

Important station removal ideas include:

### Remove Customer With Preceding Station

If a customer is removed, the charging station immediately before it may no longer be needed.

Example:

```text
... -> station -> customer -> ...
```

If the customer is removed, the station visit may become redundant.

### Remove Customer With Succeeding Station

Similarly, if a customer is removed, the station immediately after it may no longer be necessary.

### Worst-Charge Usage Station Removal

Remove stations visited when the vehicle still has a relatively high battery level. The intuition is that charging too early may be inefficient.

### Full Charge Station Removal

Promote partial recharge behavior by removing station visits where full charging occurs and checking whether a better partial-recharge route can be reconstructed.

These operators are important because in EVRP, charging station visits are not ordinary customer visits. Their usefulness depends on battery state, future route segments, and time-window feasibility.

## Insertion Operators

After removing nodes, the algorithm repairs the solution by reinserting customers and charging stations.

Customer insertion mechanisms include:

- greedy insertion;
- regret-2 insertion;
- regret-3 insertion;
- time-based insertion.

A key EV-specific issue is that a customer insertion may be feasible for time windows but infeasible for battery. In that case, station insertion is needed.

Station insertion mechanisms include:

### Greedy Station Insertion

Find the first point where battery becomes negative, then insert a charging station before that point.

### Greedy Station Insertion With Comparison

Compare nearby station insertion positions and choose the one that increases route distance least.

### Best Station Insertion

Consider several possible arcs before the battery-infeasible point and choose the best feasible station insertion.

These mechanisms show how EVRP heuristics repair battery infeasibility: they do not merely reject an infeasible route, but try to insert charging stations intelligently.

## Acceptance Rule

The new solution is accepted using a Simulated Annealing criterion.

This means the algorithm can sometimes accept a worse solution temporarily. The reason is to escape local optima. A route that is slightly worse now may lead to better repairs or station placements later.

This connects to Schneider et al.'s use of simulated-annealing-style deterioration: both papers use controlled acceptance of worse solutions to improve exploration.

## Main Findings

The paper reports that:

1. ALNS can find high-quality solutions on Schneider EVRPTW benchmark instances.

2. Partial recharge may significantly improve routing decisions compared with full recharge.

3. Variable partial recharge generally performs better than fixed partial recharge levels such as charging to 30%, 40%, or 50%.

4. Partial recharge can reduce unnecessary charging time, which can help meet tight time windows.

5. The additional flexibility of partial recharge increases computational complexity because recharge amount must be determined along with route structure.

## Key Takeaways

1. Full recharge is a simplifying assumption, not always the best operational decision.

2. Partial recharge introduces a new continuous decision: how much battery to charge at a station.

3. EVRP route feasibility depends on both the position of charging stations and the recharge amount at those stations.

4. Station removal and insertion deserve special operators. Treating stations exactly like customers loses important energy-feasibility structure.

5. For future DRL work, partial recharge is harder than full recharge because the action space is no longer purely discrete.

## Connection To This Project

The current project targets Lin et al. (2021), which follows the full-recharge EVRP-TW setting. Therefore, Keskin and Catay should not replace the main replication target.

However, it is useful for two reasons.

### 1. It Clarifies The Design Space

There are multiple EVRP-TW variants:

```text
EVRPTW-FR: full recharge
EVRPTW-PR: partial recharge
```

Lin et al. is closer to EVRPTW-FR. Keskin and Catay explain what changes when this assumption is relaxed.

### 2. It Suggests Future Improvement Directions

A possible long-term innovation is to extend the model from full recharge to partial recharge.

For a heuristic solver, this could mean:

```text
insert station + choose recharge amount
```

For a DRL solver, this is more difficult because the policy would need to choose:

```text
next node
+ recharge amount if next node is a station
```

That would turn the action into a mixed discrete-continuous decision.

## Connection To Week 4 GA Work

The Week 3 GA baseline is still VRPTW, not EVRPTW. It has no battery state and no charging stations. Therefore, implementing full partial recharge now would be too large for Week 4.

But this paper still gives a useful roadmap. A staged extension could be:

```text
Stage 1: report time-window violations explicitly
Stage 2: add simple route-level battery feasibility
Stage 3: add charging station insertion
Stage 4: add full recharge
Stage 5: add partial recharge
```

For Week 4, the most realistic contribution remains explicit violation metrics and penalty sensitivity. Keskin and Catay supports this choice because their ALNS also relies on feasibility-aware repair and careful handling of battery/time-window trade-offs.

## Useful Sentences For Report

Keskin and Catay (2016) extend Schneider et al.'s EVRPTW by relaxing the full-recharge assumption and allowing vehicles to recharge partially. This is more realistic because full recharge may waste time when only a small amount of energy is needed to finish a route or reach the next station.

The paper shows that charging decisions interact strongly with time-window feasibility: charging more improves battery safety but can make the vehicle late. This reinforces the need to report feasibility and violation metrics separately from aggregate route cost.

For the current project, partial recharge is better treated as a future extension rather than an immediate Week 4 implementation target. The current GA baseline must first be extended with explicit feasibility evaluation and, later, basic battery and charging-station logic before partial recharge can be tested meaningfully.

