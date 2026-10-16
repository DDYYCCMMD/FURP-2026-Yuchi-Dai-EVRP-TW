# Research Showcase Poster Presentation Script

## Main script (about 3 minutes)

Hello, my name is Yuchi Dai. My project studies the Electric Vehicle Routing Problem with Time Windows, or EVRPTW.

In this problem, vehicles must serve every customer within a specified time window. Electric vehicles add another constraint: the battery must remain feasible throughout the route, and charging-station visits may be required. This means that a short route is not necessarily a valid route.

My research question was: can a compact Adaptive Large Neighbourhood Search, or ALNS, consistently produce strictly feasible electric-vehicle routes, and what extra operational cost is introduced by the battery constraints?

The method is shown in the pipeline on the right. It begins with a feasible solution and repeatedly removes and reinserts customers. The destroy operators include random, worst, and related removal, while the repair operators use greedy or regret-based insertion. When battery constraints are enabled, a charging-station repair step inserts a full-recharge stop where necessary.

The key design choice is the unified feasibility evaluator. The same evaluator checks customer coverage, route structure, capacity, time windows, and battery state during construction, repair, local search, acceptance, and final auditing. The objective is lexicographic: it first minimises the number of vehicles and then the total distance.

For the experiment, I used 18 small Schneider benchmark instances with 5, 10, and 15 customers. Each configuration was tested with three random seeds and 1,000 ALNS iterations. There were five configurations and 270 runs in total. Of these, 216 runs included battery constraints.

The first main result is correctness. All 216 battery-enabled runs were strictly feasible when the saved routes were evaluated again.

The second result is the operational cost of electrification. In 28 of the 54 matched comparisons, the EV solution required more vehicles than the corresponding non-battery solution, and it never required fewer. When both solutions used the same fleet size, the EV route was longer in 23 of 26 comparisons, with a mean distance increase of 12.419.

The third result is computational cost. The EV-to-non-EV runtime ratio increased from 5.65 at 5 customers to 20.22 at 15 customers. Charging repair and repeated feasibility evaluation therefore become increasingly expensive as the instance size grows.

Finally, the ablation study shows that local search had only a small quality benefit on these instances. The full method won 7, tied 45, and lost 2 comparisons against the version without local search. Removing local search reduced runtime by 47.3 percent. In addition, 95.6 percent of iterations produced equal-objective candidates, which suggests limited search diversity.

Overall, the project demonstrates a reliable feasibility-first ALNS pipeline for the tested full-recharge EVRPTW instances. The main limitation is that the experiment uses only small instances, three seeds, and greedy full-recharge station insertion. A useful next step would be to design charging-specific neighbourhoods and test larger instances.

Thank you. I am happy to answer any questions.

## One-minute version

Hello, my name is Yuchi Dai. This project studies the Electric Vehicle Routing Problem with Time Windows. The challenge is to serve every customer within its time window while maintaining route capacity and battery feasibility.

I developed a feasibility-first ALNS solver with adaptive destroy-and-repair operators, full-recharge station insertion, simulated annealing, and a unified evaluator. The evaluator checks the same constraints throughout construction, search, and final auditing.

I tested five configurations on 18 small Schneider instances, using three seeds and 1,000 iterations per run. All 216 battery-enabled runs were strictly feasible. Compared with the corresponding non-battery routes, EV routes used more vehicles in 28 of 54 matched runs and never used fewer. For equal-fleet comparisons, EV routes were longer in 23 of 26 cases. The EV runtime penalty also grew from 5.65 times at 5 customers to 20.22 times at 15 customers.

The main conclusion is that strict EV feasibility can be maintained reliably, but battery constraints increase both routing and computational cost. Future work should focus on charging-specific neighbourhoods and larger benchmark instances.

## Likely questions and short answers

### Why did you use ALNS instead of reinforcement learning?

The earlier learning and genetic-algorithm baselines did not provide a complete, auditable treatment of time windows, battery use, and charging stations. ALNS allowed me to enforce strict feasibility directly and complete a controlled experiment within the summer project.

### What does "strictly feasible" mean here?

Every customer is served exactly once, every route begins and ends at the depot, and capacity, time-window, and energy violations are all zero.

### Why are there 270 total runs but only 216 battery-enabled runs?

There were five configurations. Four were EVRPTW configurations and one was a non-battery VRPTW comparison. With 18 instances and three seeds, the four EV configurations produced 216 runs, while all five configurations produced 270 runs.

### What is the difference between the EV and non-EV comparison?

They use the same customer data and the same general search framework. The EV version additionally enforces battery feasibility and may insert charging stations, so the comparison isolates the effect of those constraints.

### Does 216 out of 216 prove the method always works?

No. It establishes strict feasibility on the tested small benchmark instances and seeds. The poster deliberately limits the claim to that experimental scope.

### Why did local search save so little quality?

The small instances and deterministic feasible constructor often reached the same objective. Most iterations produced equal-objective candidates, so the generic relocate and 2-opt moves had limited room to improve the solution.

### What would you improve next?

I would add charging-station removal and replacement moves, partial-recharge decisions, stronger diversity mechanisms, and experiments on larger instances with more seeds.

## Chinese memory outline

1. **Problem:** time windows plus capacity plus battery; short does not mean feasible.
2. **Method:** ALNS destroy and repair, charging repair, unified evaluator, fleet-first objective.
3. **Experiment:** 18 instances, 3 seeds, 1,000 iterations, 5 configurations, 270 runs.
4. **Correctness:** 216 out of 216 battery-enabled runs strictly feasible.
5. **Operational cost:** 28 out of 54 used more EVs; equal-fleet EV routes longer in 23 out of 26.
6. **Runtime:** 5.65 times to 20.22 times as size grows.
7. **Ablation:** no-local-search version was 47.3 percent faster; 95.6 percent equal-objective iterations.
8. **Limitations:** small instances, three seeds, full recharge, greedy station insertion.
