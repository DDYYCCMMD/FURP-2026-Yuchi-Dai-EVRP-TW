# Summer Research Project 2026 — Full-Recharge ALNS for EVRP-TW

> **Faculty Undergraduate Research Practice (FURP)**
> Undergraduate Research Group · Faculty of Science and Engineering · University of Nottingham Ningbo China

---

## Project Info

| Field | Your entry |
|---|---|
| Student name(s) | Yuchi Dai |
| Project title | A Feasibility-First Full-Recharge ALNS for Electric Vehicle Routing with Time Windows |
| Project tag | EVRP-TW |
| Track | Research |
| Supervising faculty | Tianxiang Cui |
| Team or individual | Individual |
| Initial research reference | Lin, Ghaddar & Nathwani (2021). Deep Reinforcement Learning for Electric Vehicle Routing Problem with Time Windows. *IEEE TITS*. DOI: [10.1109/TITS.2021.3105232](https://doi.org/10.1109/TITS.2021.3105232) |
| Final implementation focus | Method-level ALNS adaptation using the full-recharge EVRPTW assumptions of Schneider, Stenger & Goeke (2014), informed by Keskin & Catay (2016) |

**One-line summary:** Developing and evaluating a feasibility-first ALNS solver for the full-recharge Electric Vehicle Routing Problem with Time Windows, with explicit capacity, time-window, battery, and charging-station checks.

The project began with a deep-reinforcement-learning reproduction plan. After
baseline work exposed missing EVRP-TW feasibility support, the final summer
scope shifted to a route-based ALNS implementation that could be audited and
evaluated end to end. The final claim is a verified method-level adaptation,
not a complete numerical reproduction of Lin et al. (2021) or Keskin and Catay
(2016).

## Final Summer Report

The completed summer-project report is available here:

- **[`FINAL_SUMMER_REPORT.md`](FINAL_SUMMER_REPORT.md)** — final project scope,
  method, experiments, results, limitations, and reproducibility evidence.
- [`docs/week06_alns_evrptw_report.md`](docs/week06_alns_evrptw_report.md) —
  detailed Week 6 technical report supporting the final report.

## Research Showcase Poster

- **[`FURP_Showcase.pdf`](FURP_Showcase.pdf)** — reviewed A1 portrait poster for the
  2026 FoSE Research Showcase.
- [`poster/poster.tex`](poster/poster.tex) — editable LaTeX source.
- [`poster/PRESENTATION_SCRIPT.md`](poster/PRESENTATION_SCRIPT.md) — three-minute
  and one-minute presentation scripts, likely questions, and a Chinese memory
  outline.

---

## Start Here

If you are reading this repository for the first time:

1. Read [`FINAL_SUMMER_REPORT.md`](FINAL_SUMMER_REPORT.md) for the completed
   project, main results, limitations, and evidence.
2. View [`FURP_Showcase.pdf`](FURP_Showcase.pdf) for the research-showcase
   summary and use [`poster/PRESENTATION_SCRIPT.md`](poster/PRESENTATION_SCRIPT.md)
   for the accompanying presentation.
3. Read this `README.md` for the repository structure and project history.
4. Read [`docs/00_weekly.md`](docs/00_weekly.md) for the chronological progress
   record.
5. Read [`labs/week6/README.md`](labs/week6/README.md) to run or inspect the
   final full-recharge ALNS-EVRPTW implementation.
6. Read [`src/README.md`](src/README.md) for the earlier learning-based
   EVRP-TW development path.

---

## Mandatory structure

This structure is **mandatory** — please keep it intact.

```
/docs
 ├── 00_weekly.md         ← update EVERY week: progress, challenges, next steps
 └── meeting_notes/       ← key takeaways from all team meetings
/src                      ← your code / experiments / materials
FURP_Showcase.pdf         ← your poster / presentation PDF, in the repo root
```

- **`docs/00_weekly.md`** — your weekly progress log. This is the first thing we check.
- **`docs/meeting_notes/`** — one file per meeting with key takeaways and action items.
- **`src/`** — all your code, scripts, notebooks, and experiment materials.
- **`FURP_Showcase.pdf`** — your final poster, placed in the **repo root** with this exact filename.

---

## Current repository map

The repository now contains both the mandatory FURP structure and additional research folders used for baseline recreation and EVRP-TW development.

| Path | Purpose |
|---|---|
| [`FINAL_SUMMER_REPORT.md`](FINAL_SUMMER_REPORT.md) | Complete final summer-project report and primary submission record |
| [`FURP_Showcase.pdf`](FURP_Showcase.pdf) | A1 portrait Research Showcase poster |
| [`poster/`](poster/) | Editable poster source, Nottingham theme assets, and presentation script |
| [`docs/`](docs/) | Research logs, reading notes, meeting notes, experiment reports, and result summaries |
| [`docs/00_weekly.md`](docs/00_weekly.md) | Weekly progress log; update every week |
| [`docs/week02_method_comparison.md`](docs/week02_method_comparison.md) | Week 2 comparison of POMO and GA baselines |
| [`docs/week03_experiment_report.md`](docs/week03_experiment_report.md) | Week 3 GA-VRPTW search-budget experiment report |
| [`docs/week04_extension_report.md`](docs/week04_extension_report.md) | Week 4 feasibility-aware GA-VRPTW extension report |
| [`docs/week05_repair_report.md`](docs/week05_repair_report.md) | Week 5 repair-aware GA-VRPTW ablation report |
| [`docs/week06_alns_evrptw_report.md`](docs/week06_alns_evrptw_report.md) | Week 6 full-recharge ALNS-EVRPTW experiment report |
| [`docs/week04_schneider2014_note.md`](docs/week04_schneider2014_note.md) | Week 4 detailed reading note on Schneider et al. (2014) |
| [`docs/week04_keskin2016_note.md`](docs/week04_keskin2016_note.md) | Week 4 detailed reading note on Keskin & Catay (2016) |
| [`docs/figures/week04/`](docs/figures/week04/) | Figures for the Week 4 report |
| [`docs/figures/week05/`](docs/figures/week05/) | Figures for the Week 5 repair report |
| [`docs/figures/week06/`](docs/figures/week06/) | Method diagrams and experimental figures for Week 6 |
| [`src/`](src/) | Main project code for EVRP-TW environment, models, training, and evaluation |
| [`src/envs/`](src/envs/) | Custom EVRP-TW environment implementation |
| [`src/models/`](src/models/) | Custom EVRP-TW embeddings and model components |
| [`labs/`](labs/) | Weekly lab tasks and cloned external baseline repositories |
| [`labs/README.md`](labs/README.md) | Guide for using `labs/` and recording experiment reports in `docs/` |
| [`labs/tasks/`](labs/tasks/) | Weekly task briefs |
| [`labs/week6/`](labs/week6/) | Full-recharge ALNS-EVRPTW implementation, tests, and experiment runners |
| [Schneider EVRPTW benchmark](https://data.mendeley.com/datasets/h3mrm5dhxw/1) | External benchmark data used by the final experiments; download locally into `data/schneider_instances/` |
| [`resource/`](resource/) | Papers and BibTeX references |
| [`results/`](results/) | Generated experiment summaries and outputs |

After completing an experiment, write the final summary in `docs/`, not only in terminal output or raw result files.

---

## Current progress snapshot

Completed so far:

- Environment setup and initial smoke tests for RL4CO and PyVRP.
- Literature collection and reading notes for EVRP-TW, Attention Model, POMO, and related VRP methods.
- Schneider EVRPTW benchmark instances used locally from the published
  [Mendeley Data record](https://data.mendeley.com/datasets/h3mrm5dhxw/1).
- Week 2 baseline recreation completed for the original POMO repository on `TSP20`, `TSP100`, and `CVRP100`.
- Week 2 GA-VRPTW baseline recreation completed on Solomon `R101` and `C204`.
- Week 3 GA-VRPTW controlled search-budget experiment completed on Solomon `R101`, `C101`, and `RC101`, with `ind_size=25/50` and repeated seeds.
- Week 4 reading notes completed for Schneider et al. (2014) and Keskin & Catay (2016), focusing on EVRP-TW feasibility, recharging stations, full recharge, and partial recharge.
- Week 4 GA-VRPTW feasibility-aware extension completed: explicit `late_customer_count`, `total_lateness`, and `max_lateness` metrics were added, and 72 delay-penalty sensitivity runs were recorded.
- Week 5 repair-aware GA-VRPTW extension completed: relocate and bounded 2-opt repair were compared with the penalty-only baseline across 27 runs on `R101`, `C101`, and `RC101`.
- Week 6 full-recharge ALNS-EVRPTW vertical slice completed: a unified capacity/time-window/energy evaluator, charging-station repair, adaptive destroy/repair operators, SA, and local search were validated across 270 fixed-iteration formal runs.
- All 216 battery-enabled Week 6 runs are strictly feasible; the formal results, analysis workbook, eight report figures, and component ablations are documented in [`docs/week06_alns_evrptw_report.md`](docs/week06_alns_evrptw_report.md).
- Main EVRP-TW implementation started under [`src/`](src/), including custom environment, embeddings, training, and evaluation scripts.

Next research direction:

- Preserve Week 6 as the fixed full-recharge baseline and improve search diversity with station removal/reposition or an energy-aware destroy operator.
- Extend evaluation to larger Schneider instances before drawing broader performance conclusions.
- Treat partial charging as a later controlled extension after the full-recharge baseline remains stable at larger scale.
- Continue reporting objective value, feasibility status, constraint violations, and runtime together.

Generated training and experiment artifacts:

- `lightning_logs/` is generated by PyTorch Lightning / RL4CO training or smoke tests and is treated as run output rather than source code.
- `labs/week*/` cloned baseline repositories and generated CSV/log outputs are exploratory lab artifacts. Human-readable conclusions should be written in `docs/`.

---

## The three rules for your certificate

To earn your FURP certificate, **all three** must be satisfied:

1. **Attend > 50%** of programme activities (weekly meetings, workshops, scheduled sessions — online or in person).
2. **Submit a poster** — place it as `FURP_Showcase.pdf` in this repo root.
3. **Present at the Poster Showcase** — in person (strongly preferred), or send a stand-in if you truly cannot attend.

> Miss any one of the three, and the certificate is not awarded this round.

**Research Track — minimum for certification:** successful replication of a cited paper with at least **10% innovation** (reproduce the work *and* add something new).

---

## Weekly cadence

Every week, you should:

- ✅ Update [`docs/00_weekly.md`](docs/00_weekly.md)
- ✅ Log meeting notes in [`docs/meeting_notes/`](docs/meeting_notes/)
- ✅ Attend the weekly meeting (online or in person)

Consistent weekly engagement is the backbone of a successful FURP project — and it feeds directly into your attendance (Rule 1).

---

## Leave & withdrawal

Any **leave of absence** or **withdrawal** must be notified to us **by email** — a verbal or chat message is not sufficient.

- **Leave:** email *before* the session where possible, state the date(s) and reason. Note that leave still counts against the >50% attendance rule.
- **Withdrawal:** email us to formally withdraw so we can free your project slot and update records.
- **Switching tracks:** email the project lead with the subject *"Project Transfer Request"* and CC your supervising faculty member.

> No email = no record. Always put leave and withdrawal in writing.

---

## Quick checklist

- [x] Forked the template and renamed the repo (`FURP-2026/Yuchi-Dai-EVRP-TW`)
- [x] Made the repo public **or** shared it with the research group
- [x] Filled in the *Project Info* table above
- [x] Started `docs/00_weekly.md`
- [x] Created my first file in `docs/meeting_notes/`
- [x] (By Showcase) Added `FURP_Showcase.pdf` to the repo root

---

## Reference Repositories

| Repository | Description |
|---|---|
| [Dr-Cui-s-Undergrade-Group/VRP-EVRP-Project-Hub](https://github.com/Dr-Cui-s-Undergrade-Group/VRP-EVRP-Project-Hub) | Supervisor's hub — benchmarks, metrics guidance, and project resources |

---

*Bridging the gap between classroom knowledge and cutting-edge research.*
