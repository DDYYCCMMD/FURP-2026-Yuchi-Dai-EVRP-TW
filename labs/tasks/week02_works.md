# Week 2 Lab: Baseline Methods Recreation and Comparison

## Objectives

This week each team should review some papers and try to recreate the methods proposed in these papers, and write a short overview/conclusion on comparing results and methodologies used in your experiments.

You should try different problem scales (e.g., 50, 100, 200 clients) and record and analyze the results.

## Step 1: POMO approach

[github](https://github.com/yd-kwon/POMO)
[paper](https://proceedings.neurips.cc/paper/2020/hash/f231f2107df69eab0a3862d50018a9b2-Abstract.html)

The original POMO implementation is solely for CVRP, for E and TW constraints you have to implement them yourself.

## Step 2: GA approach

[github](https://github.com/iRB-Lab/py-ga-VRPTW.git)

Also, you have to implement E constraint yourself.

## Step 3: UAV-Truck Problem

[Electric truck-based robot delivery problem with nonlinear charging](https://www.sciencedirect.com/science/article/pii/S1366554526002978)
A OR + ALNS hybrid solution, you can try to recreate the OR part first.

[Real-time order dispatch for on-demand food-delivery platforms with a mixed fleet of drones and couriers](https://www.sciencedirect.com/science/article/pii/S0191261526000834)
A OR(MILP) + graph solution, you can try to recreate the OR part first.

## Step 4: Method Comparison and Record

For each recreated method, record:
- Instance problem scale (e.g., 50, 100, 200 clients);
- Objective value achieved;
- Feasibility status under added constraints (if E or TW are added);
- Runtime and convergence details.

## Step 5: Reflection

Write a short overview/conclusion:
- How do the results (objective value, runtime) compare across the different methodologies (POMO, GA, OR)?
- What were the main challenges in adding E and/or TW constraints to the baselines?
- What insights were gained for structuring our target EVRP-TW models?

## Deliverables

- Code for the recreated baselines, including any constraint implementations.
- A results table recording objective values, runtimes, and feasibility for at least two differing problem scales.
- A brief overview/reflection document comparing the tested methodologies.