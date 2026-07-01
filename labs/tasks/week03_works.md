# Week 3 Lab: Experiment Design, Evaluation, and Report Writing

## Objectives

This week, each team should move from "recreating a method" to "evaluating a method properly".

By the end of this lab, you should be able to:

- Design a fair comparison between your method and one or more baselines.
- Run controlled experiments instead of only collecting random solver outputs.
- Explain what your metrics mean and what conclusions can or cannot be drawn from them.
- Write a short but convincing experimental report.

## Suggested Problem Directions

Choose one main direction for your experiments.

### 1. Truck-Drone Problem

You may study one of the following:

- OR-based method: https://doi.org/10.1109/TITS.2022.3181282
- Heuristic-based method: https://doi.org/10.1109/TITS.2020.2992549


### 2. ECVRPTW Problem

You may either:

- search for a paper by yourselves and recreate one method; or
- continue from the papers mentioned last week.

This topic has a large amount of literature, so choosing a method with clear inputs, outputs, and evaluation settings is more important than choosing the most advanced paper.

## Main Task

Your task this week is not only to "make the code run". Your task is to show, with evidence, how well a method works and under what conditions it works better or worse.

That means your repository should include:

- the code you used for the experiments;
- the instance settings or datasets you tested on;
- the raw outputs or logs;
- a cleaned summary table;
- a short report that explains the results.

## How To Conduct the Experiment

### Step 1: Define the Comparison Target

Before running anything, state clearly:

- What method are you testing?
- What baseline are you comparing against?
- What is the main difference between them?
- What question are you trying to answer?

Examples of valid experiment questions:

- Does method A achieve a better objective value than baseline B on medium-size instances?
- Does adding time-window constraints make the heuristic much slower?
- Is the OR model still solvable when instance size increases from 50 customers to 100 customers?
- Does the drone-assisted setting reduce total delivery cost compared with truck-only routing?

If you cannot state the question in 1 to 3 sentences, your experiment is probably still too vague.

### Step 2: Choose Fair Test Cases

Your comparison must be fair. This usually means:

- using the same instance set for all methods;
- using the same distance matrix / coordinate data;
- using the same objective definition;
- using the same stopping condition if possible.

You should test at more than one scale. For example:

- small: 20 to 50 customers;
- medium: 50 to 100 customers;
- large: 100+ customers.

If your solver is still unstable, it is acceptable to focus on small and medium instances first, but you should say so honestly in the report.

### Step 3: Decide What to Record

At minimum, record the following for every run:

- instance name or size;
- method name;
- objective value;
- runtime;
- feasibility status;
- number of vehicles used, if relevant;
- constraint violations, if any;
- random seed, if the method is stochastic.

If available, also record:

- best solution found;
- gap to baseline or best-known result;
- convergence curve or improvement over time;
- number of iterations / generations / search steps.

Important:

- "Objective value" alone is not enough.
- "Runtime" alone is not enough.
- "Feasible or infeasible" is very important, especially for ECVRPTW and truck-drone problems.

### Step 4: Run Repeated Trials When Needed

If your method includes randomness, do not report only one lucky run.

For stochastic methods, try to run each setting multiple times, for example:

- 3 runs for a quick check;
- 5 runs for a basic comparison;
- 10 runs if runtime is affordable.

Then report summary statistics such as:

- best result;
- average result;
- standard deviation, if possible.

This helps show whether a method is consistently good or only occasionally good.

### Step 5: Organize Results Clearly

Do not only upload `.json` files or raw terminal outputs.

Create at least one readable results table. A good table may look like this:

| Instance | Size | Method | Feasible | Objective | Runtime (s) | Notes |
|---|---:|---|---|---:|---:|---|
| A-n32 | 32 | Baseline GA | Yes | 842.5 | 12.8 | Stable |
| A-n32 | 32 | Improved GA | Yes | 801.3 | 14.2 | Better objective |
| B-n64 | 64 | Baseline GA | No | - | 30.0 | Violates TW |
| B-n64 | 64 | Improved GA | Yes | 1562.4 | 28.7 | Feasible |

If you have many runs, also add an aggregated table:

| Size Group | Method | Feasible Rate | Avg. Objective | Avg. Runtime (s) |
|---|---|---:|---:|---:|
| Small | Baseline | 100% | 812.4 | 10.1 |
| Small | Proposed | 100% | 790.8 | 12.6 |
| Medium | Baseline | 60% | 1498.2 | 25.7 |
| Medium | Proposed | 100% | 1461.5 | 29.3 |

### Step 6: Analyze, Do Not Just Display

After producing tables, explain them.

At minimum, answer:

- Which method gives better objective values?
- Which method is faster?
- Which method is more robust in finding feasible solutions?
- How does performance change when instance size grows?
- What trade-off do you observe between quality and runtime?

Good analysis is specific. For example:

- "Our improved heuristic is about 10 to 15 percent slower than the baseline, but it remains feasible on all medium-size instances, while the baseline fails on 2 out of 5 instances."

Weak analysis is vague. For example:

- "Method A is better."

You must say better in what sense.

### Step 7: Discuss Failure Cases

Failure cases are useful and should not be hidden.

If your method fails, discuss:

- when it fails;
- why it may fail;
- whether the failure is due to modeling, coding, parameter setting, or computational limits.

Examples:

- the MILP becomes too slow after 100 customers;
- the heuristic often produces infeasible solutions under tight time windows;
- the battery constraint implementation may be too strict or incorrect;
- the drone synchronization rule makes the search space much harder.

This kind of reflection is often more valuable than only showing a successful small instance.

## How To Write the Report

Your report does not need to be long, but it must be structured and evidence-based.

A suggested structure is below.


### Experimental Setup

Explain:

- what instances or datasets you used;
- what scales you tested;
- what hardware or environment you used, if relevant;
- what stopping criteria you used;
- what metrics you recorded.

If you simplified anything from the original paper, say it clearly here.

For example:

- "We implemented the core GA framework from the paper, but replaced the original local search with a simpler 2-opt improvement."

That is acceptable as long as it is transparent.

### Results

Present:

- one or more tables;
- optional figures such as convergence plots;
- a short summary of the main numerical findings.

Do not paste raw logs into the main report. Logs can go into an appendix or separate file.

### Discussion

This is the most important part.

Discuss:

- why one method performed better or worse;
- whether the improvement is consistent or only appears on some instances;
- whether the runtime increase is acceptable;
- what constraints are hardest for the solver;
- what limitations remain in your implementation.

Try to connect the results to the algorithm design. For example:

- "The improved feasibility on tight TW instances likely comes from the repair operator, which explicitly removes late-arrival violations."

### Conclusion

Write 3 to 6 sentences summarizing:

- what you tested;
- what you found;
- what the next step should be.

Good conclusions usually mention both strengths and limitations.

## Common Problems To Avoid

Please avoid the following:

- only showing one run of a random algorithm;
- comparing methods on different instances;
- reporting numbers without explaining what they mean;
- claiming one method is better without discussing runtime or feasibility;
- copying AI-generated outputs into the repo without checking them;
- including raw result files but no summary table;
- writing a report that only describes the code and not the experimental findings.

## Minimum Deliverables

Each team should submit:

- code for the tested method and baseline, or a clear explanation if one baseline is taken from an external repository;
- experiment records for multiple instances or scales;
- at least one cleaned summary table;
- a short report with setup, results, discussion, and conclusion.

## Recommended Deliverables

If you want to do a stronger job, also include:

- repeated trials for stochastic methods;
- visualizations such as convergence curves or runtime-vs-quality plots;
- ablation experiments, such as removing one operator or one constraint-handling strategy;
- a brief error analysis of failed cases.