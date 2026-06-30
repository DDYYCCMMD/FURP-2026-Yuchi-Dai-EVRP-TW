# Labs Guide for Humans and AI Assistants

This folder contains weekly lab tasks, cloned baseline repositories, and experiment materials used to reproduce and compare methods. It is a working area for learning from external code before moving stable project code into `src/`.

## Role Of `labs/`

Use `labs/` for:

- weekly task briefs;
- cloned baseline repositories referred to `/tasks`;
- exploratory baseline recreation;
- lab-specific scripts or notes that are not yet part of the main project implementation.

Do not use `labs/` as the final place for written experiment reports. After an experiment is completed, write the human-readable report in `docs/`.

## Current Structure

| Path | Purpose |
|---|---|
| `labs/tasks/` | Weekly lab task briefs |
| `labs/week2/pomo/` | Cloned POMO baseline repository from `yd-kwon/POMO` |
| `labs/week2/ga_evrptw/` | Cloned GA-VRPTW baseline repository |
| `labs/week3/` | Reserved for Week 3 lab materials and experiments |

## How To Use This Folder

For each lab week:

1. Read the task brief in `labs/tasks/`.
2. Clone or place external baseline repositories under the matching week folder.
3. Run the baseline experiments inside `labs/`.
4. Keep raw outputs in the baseline repo's own `result/` or `results/` folder, or in project-level `results/` if a summary file is created.
5. Write the final experiment summary in `docs/`.
6. Update `docs/00_weekly.md` with progress, results, blockers, and next steps.

## Reporting Rule

Terminal output is not the final record.

After running a lab experiment, record the important result in `docs/`, including:

- method or baseline name;
- source repository or paper;
- command used;
- problem type, such as TSP, CVRP, VRPTW, or EVRP-TW;
- instance name and scale;
- objective value or score;
- feasibility status;
- runtime and hardware / mode;
- constraints covered;
- limitations and next steps.

Objective value alone is not enough. For routing problems, always mention feasibility and which constraints were actually modelled.

## Week 2 Example

The Week 2 task is defined in:

```text
labs/tasks/week02_works.md
```

The baseline repositories are:

```text
labs/week2/pomo
labs/week2/ga_evrptw
```

The final written comparison should be recorded in:

```text
docs/week02_method_comparison.md
```

The weekly progress summary should be recorded in:

```text
docs/00_weekly.md
```

This is the expected pattern for future lab tasks.

## Difference Between `labs/`, `src/`, And `docs/`

| Folder | Role |
|---|---|
| `labs/` | External baselines, lab tasks, exploratory reproduction |
| `src/` | Maintained project code written for this EVRP-TW project |
| `docs/` | Research notes, result tables, weekly logs, final experiment reports |

If an external baseline becomes part of the maintained project implementation, rewrite or adapt it into `src/` rather than relying on a cloned repository directly.

## Guidance For AI Assistants

Before helping with a lab task:

- read the relevant file in `labs/tasks/`;
- inspect the corresponding `labs/weekN/` folder;
- avoid mixing final reports into cloned repositories;
- place final summaries in `docs/`;
- update `docs/00_weekly.md` after meaningful progress;
- keep raw benchmark data and cloned repository code in place unless the user explicitly asks to reorganize them.
- Week0N task does't must refer to corresponding week log.

When a user provides terminal output, help convert it into a clean result table and reflection in `docs/`.

## Important Rule: Do Not Use `src/` For Lab-Only Work

For weekly lab tasks, do not create or modify files under `src/` unless the user explicitly says that the work should become part of the final EVRP-TW implementation.

Use this separation:

- `labs/`: weekly tasks, cloned repositories, baseline reproduction, exploratory code
- `docs/`: experiment reports, result tables, reflections
- `src/`: final project implementation and replication code only

If an AI assistant is unsure where to put new code for a weekly task, it should ask first. The default location for weekly task code is `labs/weekN/`, not `src/`.
