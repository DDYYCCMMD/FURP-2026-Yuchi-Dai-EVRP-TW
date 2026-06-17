# VRP, EVRP-TW, and Truck-Drone Routing 

Undergraduate SEP summer research project hub for learning-based and hybrid optimization in constrained logistics.

[SEP background](https://www.nottingham.edu.cn/en/press-release/news-article.aspx?id=0e3d7273-3589-49d2-97db-05fc07893909&language=en-GB) | [English outline](docs/project_outline_en.md) | [中文大纲](docs/project_outline_zh.md) | [Benchmarks and metrics](docs/benchmarks_metrics_bilingual.md) | [References](docs/sota_demo_references.md) | [Week 1 lab](labs/week01_setup.md)

---

## Project Brief

This repository supports two undergraduate research topics:

1. **Deep Reinforcement Learning for Electric Vehicle Routing with Time Windows (EVRP-TW)**  
   Study how a learning-based or hybrid method can construct feasible routes under customer time windows, battery limits, and charging constraints.

2. **Ground-Air Collaborative EVRP-TW: Hybrid Optimization for Truck-Drone Delivery**  
   Extend routing from a single ground fleet to coordinated truck-drone delivery, where launch, recovery, synchronization, energy, and service-time constraints all matter.

The goal is not to invent a world-class solver in one summer. The goal is to build a reproducible research workflow: understand a problem variant, run a reliable baseline, evaluate feasibility and cost, then test one improvement with fair comparisons.

## What Students Will Build

Each team should finish with:

- a clear problem definition and data format;
- one reproducible baseline solver or policy;
- metrics for objective value, feasibility, violations, and runtime;
- at least one improvement or extension;
- failure cases showing why a route becomes infeasible or inefficient;
- a final report and 5-8 minute demo video.

## Recommended Tracks

| Track | Best for students interested in | Suggested first baseline |
|---|---|---|
| Classical VRP / VRPTW | optimization, constraints, exact or heuristic solvers | OR-Tools or PyVRP |
| Deep RL for EVRP-TW | neural combinatorial optimization, policy learning | POMO / Attention Model / RL4CO |
| Hybrid EVRP-TW | combining learning with local search or heuristics | PyVRP-style solver plus learned construction or repair |
| Truck-drone collaboration | mixed fleets, synchronization, applied logistics | small custom instances plus heuristic baseline |

Students should start from classical VRP or VRPTW before adding battery, charging, and drone constraints.

## Start Here

1. Read the [English outline](docs/project_outline_en.md) or [中文大纲](docs/project_outline_zh.md).
2. Read [Benchmarks and metrics](docs/benchmarks_metrics_bilingual.md).
3. Browse [SOTA and demo references](docs/sota_demo_references.md).
4. Complete [Week 1 setup](labs/week01_setup.md) and submit the [Week 1 checkpoint](checklists/week01_checkpoint.md).
5. Keep every command, instance file, seed, output objective, feasibility status, and runtime.

## Core Research Questions

Good SEP projects can be framed around one focused question:

- How well does a classical baseline solve small CVRP or VRPTW instances?
- What changes when battery capacity and charging stations are added?
- Can a learned policy construct routes that are feasible, not just short?
- Does local search repair improve a neural solution?
- Which constraint is most responsible for infeasibility: time windows, battery, capacity, or truck-drone synchronization?

## Evaluation Minimum

Every team should report:

- objective value or total distance;
- feasibility rate;
- time-window violations;
- battery or charging violations for EVRP-TW;
- number of charges or charging time;
- makespan for truck-drone collaboration;
- runtime and hardware;
- at least 3 failure cases with explanation.

Never report objective value alone. A very short infeasible route is not a good solution.

## Suggested 8-Week Roadmap

| Week | Theme | Deliverable |
|---|---|---|
| 1 | Environment and baseline setup | smoke-test evidence |
| 2 | VRP / EVRP literature and data formats | reading notes, problem diagram |
| 3 | Reproduce one baseline | objective, feasibility, runtime logs |
| 4 | EVRP-TW constraints | metric table with time and battery violations |
| 5 | Truck-drone formulation | synchronization and constraint note |
| 6 | Hybrid or learning method | demo run on small instances |
| 7 | Improvement and ablation | baseline vs improved comparison |
| 8 | Final integration | report, slides, demo video, reproducibility package |

## High-Value References

Start with these:

- [OR-Tools routing](https://developers.google.com/optimization/routing)
- [PyVRP](https://github.com/PyVRP/PyVRP) and [PyVRP documentation](https://pyvrp.org/)
- [POMO implementation](https://github.com/yd-kwon/POMO)
- [POMO paper](https://arxiv.org/abs/2010.16011)
- [Attention, Learn to Solve Routing Problems](https://arxiv.org/abs/1803.08475)
- [RL4CO](https://github.com/ai4co/rl4co)
- [Electric Vehicle Routing Problem with Time Windows](https://doi.org/10.1287/trsc.2013.0490)

For a larger curated list, see [SOTA and demo references](docs/sota_demo_references.md).

## Videos and Demos

GitHub README pages do not reliably support embedded video playback. Use the links below, or enable GitHub Pages for [`docs/media.html`](docs/media.html) to collect video and demo pages in one browser page.

- [Google OR-Tools routing guides](https://developers.google.com/optimization/routing)
- [PyVRP examples](https://pyvrp.org/examples/index.html)
- [BCS video page: Introduction to Operations Research with Google OR-Tools](https://www.bcs.org/events-calendar/2026/march/hybrid-an-introduction-to-operations-research-with-google-or-tools/)
- [RL4CO documentation](https://rl4co.readthedocs.io/)

## How to Ask for Help

When asking a technical question, include the instance size, constraints, command, objective value, feasibility status, error log, and what you already tried. Use [How to Ask Questions](docs/asking_questions.md) or the GitHub issue template.

## Final Standard

A strong final project should explain:

- what problem variant was solved;
- what baseline was reproduced;
- which constraints were active;
- what improved or failed;
- whether the solution is feasible;
- which evidence supports the next step.

Optimization research is about trade-offs. Make the trade-offs visible.
