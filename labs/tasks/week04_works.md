# Week 4 Lab: Extend, Read More, and Explore New Experiments

## Objectives

By Week 4, some teams should already have:

- reproduced one or more baseline methods;
- run basic comparison experiments;
- written short experimental summaries.

If you have completed most of the previous weeks' tasks, then this week is for going one step further.

The main idea is:

- read more relevant papers;
- upload your reading notes;
- try new experiments beyond the minimum required reproduction;
- start thinking about how to improve or combine methods.

## Who Should Focus on This Week

This week is especially suitable for teams who:

- already have runnable code from Weeks 1 to 3;
- already produced at least some valid experimental results;
- want to improve the quality of their project instead of stopping at a basic baseline.

If your previous tasks are still incomplete, you should finish those first before spending too much time on extra exploration.

## Main Task

Choose at least one extension direction from the following:

### 1. Read More Papers and Upload Notes

After finishing the basic reproduction work, you should broaden your view.

Try to read additional papers related to:

- ECVRPTW;
- truck-drone routing;
- hybrid OR + heuristic methods;
- learning-based routing methods;
- constraint-handling strategies for EVRP / VRPTW.

Your reading notes should not be just copied abstracts. Good notes should include:

- the problem setting of the paper;
- the main method used;
- what is novel compared with simpler baselines;
- what assumptions the paper makes;
- what parts seem reproducible or difficult to reproduce;
- what ideas may be useful for your own project.

You should upload these notes to the repository in a clear format such as Markdown.

### 2. Try New Experimental Settings

Do not stop at one problem size or one instance type.

You are encouraged to test:

- larger instance scales;
- different customer distributions;
- tighter or looser time windows;
- different battery capacities or charging assumptions;
- different truck-drone coordination settings;
- different random seeds for stochastic methods.

The goal is to learn when a method works well and when it starts to fail.

### 3. Improve an Existing Method

If you already reproduced a baseline, try making one meaningful improvement.

Examples:

- add penalty terms for infeasible EV or TW solutions;
- add a repair operator for time-window violations;
- add local search such as 2-opt or swap;
- adjust mutation / crossover / neighborhood settings;
- improve the charging or energy-consumption model;
- improve route synchronization in the truck-drone setting.

You do not need to invent a completely new algorithm. A well-motivated small improvement is already valuable if you can test and explain it properly.

### 4. Combine Ideas from Different Methods

This is a good week to try hybrid thinking.

For example, you may try:

- using an OR model to generate an initial solution, then improving it with a heuristic;
- using a heuristic to repair infeasible outputs from another method;
- combining a learning-based policy with a classical post-processing step;
- comparing whether a simpler hybrid method is more practical than a more complicated pure method.

Even if the hybrid attempt does not fully work, documenting the attempt and the difficulty is useful.

## How To Read and Take Notes

When reading extra papers, focus on extracting reusable ideas instead of trying to understand every detail perfectly.

A useful reading note can follow this structure:

### Paper Information

- title;
- authors;
- venue / year;
- link or DOI.

### Problem Setting

- What exact routing problem does the paper solve?
- What constraints are included?
- What objective is optimized?

### Method Summary

- What is the main workflow?
- What are the key operators or modeling decisions?

### What Seems Useful for Our Project

- Which ideas can be borrowed directly?
- Which ideas require major adaptation?
- Which assumptions do not fit our setting?

### Reproducibility Reflection

- What seems easy to reproduce?
- What seems difficult to reproduce?
- What information is missing from the paper?

## How To Design New Experiments

If you are running new experiments this week, make sure they are still controlled and interpretable.

At minimum, define:

- what changed compared with the previous experiment;
- why you changed it;
- what metrics you will compare;
- what you expect to learn.

If you only "try something new" but cannot explain what question it answers, the experiment is still too loose.

## Suggested Deliverables

### Minimum

- at least one additional paper note uploaded to the repo;
- at least one new experiment beyond the Week 3 baseline comparison;
- a short written summary of the new findings.

### Stronger Submission

- multiple paper notes with comparison across papers;
- one meaningful method improvement or hybrid attempt;
- experiments on multiple scales or parameter settings;
- clear discussion of both successful and failed attempts.

## Reflection Questions

Use the following questions to guide your write-up:

- What did we read this week that is new compared with previous weeks?
- What new idea did we try, and why?
- Did the new experiment reveal a strength, weakness, or trade-off?
- Which methods seem most promising now for our project?
- What should be the next step: better implementation, broader experiments, or a new baseline?

## Important Reminder

This week is not about adding random complexity.

The goal is to show research progress:

- broader understanding through reading;
- deeper understanding through better experiments;
- more independent thinking through method improvement or extension.

Even a small extension is good if it is thoughtful, documented clearly, and supported by evidence.
