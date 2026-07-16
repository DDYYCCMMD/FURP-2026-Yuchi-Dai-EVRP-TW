# Week 5 Lab: Consolidate Progress and Prepare the Next Step

## Objectives

This week is a flexible consolidation week.

At this point, teams may be at different stages. Some teams may still be finishing the reproduction and experiments from previous weeks, while others may already have a working baseline and several experimental results.

The main goal is to make your project more complete, reproducible, and easier to explain.

By the end of this week, each team should have a clearer answer to these questions:

- What have we completed so far?
- What results can we trust and explain?
- What is still missing or unstable?
- What should we do next?

## Choose the Track That Fits Your Progress

You do not need to complete every task below. Choose the track that best matches your current progress.

### Track A: Complete Previous Work First

Choose this track if your work from Weeks 1 to 4 is still incomplete.

Your priority should be to finish the essential project pipeline:

- make at least one baseline method run successfully;
- prepare one or more valid test instances;
- record objective value, runtime, and feasibility;
- run a basic comparison or sensitivity experiment;
- upload a short experiment summary and the relevant code or logs.

Do not rush into a new method before the existing pipeline is usable. A small, reproducible experiment with a clear explanation is much better than a large but unfinished attempt.

### Track B: Consolidate and Improve Existing Results

Choose this track if you already have runnable code and some results.

Focus on making the current work more reliable:

- rerun important experiments to check whether the results are stable;
- fix obvious bugs, infeasible outputs, or unclear settings;
- organize raw logs into readable tables;
- add a short explanation for each experiment;
- compare the current result with a baseline, a simplified version, or a result from the paper;
- improve the README so another team member can run the code.

Useful questions include:

- Are the results reproducible with the same settings?
- Does the method remain feasible as the instance becomes larger or constraints become tighter?
- Are we comparing methods fairly?
- Can someone else understand how to reproduce our result from the repository?

### Track C: Explore One Further Idea

Choose this track only if the previous work is already reasonably complete.

Try one focused extension rather than many unrelated changes. For example:

- test a new instance scale, customer distribution, battery capacity, or time-window setting;
- add a small local-search or repair operator;
- compare different parameter settings for a heuristic;
- combine an existing method with a simple post-processing step;
- implement one idea inspired by the papers read in Week 4.

For every extension, write down:

- what you changed;
- why you changed it;
- which experiment tests the change;
- what you learned, including negative results.

## Main Task: Prepare a Project Checkpoint

Each team should upload a short project checkpoint note in Markdown. It can be stored in your team folder or alongside your experiment files.

The checkpoint should include the following sections.

### 1. Current Project Status

Briefly state:

- the problem you are studying, such as ECVRPTW or truck-drone routing;
- the method or baseline you have implemented or reproduced;
- what currently works;
- what is not finished yet.

### 2. Evidence of Progress

Include at least one result table, figure, log excerpt, or example solution.

A simple table is enough:

| Instance | Method | Feasible | Objective | Runtime (s) | Main Observation |
|---|---|---|---:|---:|---|
| Small-1 | Baseline | Yes | 842.5 | 12.8 | Produces stable feasible routes |
| Small-1 | Improved method | Yes | 801.3 | 14.2 | Better objective, slightly slower |
| Medium-1 | Baseline | No | - | 30.0 | Time-window violations |

### 3. Problems and Limitations

Be honest about the main difficulties. For example:

- the code only works on small instances;
- the baseline result from the paper has not been matched yet;
- the solution may violate battery or time-window constraints;
- the experiment is too slow to repeat many times;
- there are not enough instances for a strong comparison.

### 4. Next Step

State one or two concrete tasks for the following week. Examples:

- fix the feasibility check for battery constraints;
- add more medium-size instances;
- compare against a second baseline;
- implement a repair operator for time-window violations;
- read one paper that uses a similar hybrid method.

## Repository Organization

Use this week to clean up the repository structure if needed.

A suggested organization is:

```text
team-folder/
  README.md
  src/                 # implementation
  data/                # instances or input files
  results/             # cleaned tables and figures
  logs/                # raw outputs, if useful
  notes/               # paper notes and checkpoint note
```

You do not need to follow this structure exactly. The important point is that code, data, results, and notes should be easy to find.

## Suggested Deliverables

### Minimum

- complete at least one unfinished essential task from the previous weeks, or verify an already completed result;
- upload a short project checkpoint note;
- include at least one piece of experimental evidence;
- state the next planned task clearly.

### Recommended for Teams Ahead of Schedule

- clean and document the experiment pipeline;
- upload additional reading notes;
- run one focused new experiment or method improvement;
- discuss one limitation or failed attempt and what you will try next.

## Important Reminder

Progress is not measured only by how many algorithms you implement.

This week, a good outcome may be:

- turning an incomplete reproduction into a runnable baseline;
- turning raw outputs into a clear result table;
- finding and explaining why a method fails;
- making the repository reproducible for your teammates;
- identifying one realistic next research question.

The goal is to leave Week 5 with a solid foundation for the remaining project work.
