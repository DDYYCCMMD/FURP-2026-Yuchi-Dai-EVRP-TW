# Weekly Progress Log

> Update this file **every week**. Add a new entry at the **bottom** for each week.
> This is the first thing we check during review. Keep it honest and specific — it also feeds your attendance record (Rule 1).

**How to use:** copy the *Week template* block below for each new week. Newest week goes at the **bottom**.

---

## Week template — copy me

### Week N — YYYY-MM-DD

**Attended this week's meeting:** Yes / No (if No, did you email leave? Yes / No)

**Progress this week**
- _What did you actually do / finish?_

**Challenges & blockers**
- _What got in the way? What are you stuck on?_

**Next steps**
- _What will you do next week?_

**Hours spent (optional):** _e.g. 6h_

**Links (optional):** _commits, notebooks, docs, datasets..._

---

<!-- =================  YOUR ENTRIES BELOW  ================= -->

### Week 1 — 2026-06-08

**Attended this week's meeting:** Yes

**Progress this week**
- Attended FURP Kickoff meeting; confirmed programme rules, certificate requirements, and mandatory repo structure.
- Set up repository from the FURP template; filled in student name, project title, and track in README.
- Confirmed replication target: **Lin, Ghaddar & Nathwani (2021), "Deep Reinforcement Learning for Electric Vehicle Routing Problem with Time Windows", IEEE TITS.** (arXiv 2010.02068, DOI 10.1109/TITS.2021.3105232)
- Created and activated `evrptw` conda environment (Python 3.11.15, Anaconda).
- Installed full tool stack: PyTorch 2.12.0 (MPS/Apple Silicon), RL4CO 0.6.0, PyVRP, NumPy 2.4.6, Matplotlib 3.11.0, Lightning 2.6.5, pandas, TensorBoard.
- Confirmed MPS (Apple Silicon GPU) available — training will use on-device GPU.
- Ran and passed both smoke tests: RL4CO CVRP training (1 epoch, `lightning_logs/` generated) and PyVRP VRPTW small-instance solve (feasible solution confirmed).
- Collected 11 core papers into `resource/papers/` with BibTeX in `resource/references.bib`.
- Created `docs/reading_plan.md` with Week 2 reading schedule (11 papers, depth ratings, 7-day split).
- Wrote kickoff meeting notes in `docs/meeting_notes/2026-06-08.md`.
- Completed `checklists/week01_checkpoint.md`.

**Challenges & blockers**
- None

**Next steps**
- Read papers in order per `docs/reading_plan.md` (target: complete by 2026-06-21).
- Priority reads: Schneider 2014 (EVRP-TW formulation) and Kool 2019 (Attention Model backbone).
- Write reading notes using the template in `docs/reading_plan.md`.

**Hours spent (optional):** ~8h

**Links (optional):**
- Replication target: [arXiv 2010.02068](https://arxiv.org/abs/2010.02068)
- Meeting notes: [`docs/meeting_notes/2026-06-08.md`](meeting_notes/2026-06-08.md)
- Environment guide: [`src/README.md`](../src/README.md)
- Reading plan: [`docs/reading_plan.md`](reading_plan.md)
- Week 1 checkpoint: [`checklists/week01_checkpoint.md`](../checklists/week01_checkpoint.md)

---

### Week 2 — 2026-06-17

**Attended this week's meeting:** Yes

**Progress this week**
- Read all 11 papers in the reading plan; compiled full reading notes in `docs/reading_notes.md`.
- Confirmed implementation strategy: replicate Lin et al. (2021) *within the RL4CO framework* (extending `VRPTWEnv` to `EVRPTWEnv`) rather than from scratch, given no public code exists for the original paper.
- Identified the exact architectural differences between Lin et al. and Kool et al.: graph embedding layer, three-type node features, battery + time-window masking, and charging station visit logic.
- Compiled `docs/reference_handbook.md` consolidating problem variables, metrics, benchmarks, and SOTA overview for ongoing reference.
- Identified EVRPTW is **not yet a built-in environment in RL4CO v0.6.0** — custom environment implementation required.
- Identified two strong innovation candidates: (1) POMO-style multi-start augmentation; (2) curriculum-based training (phases: CVRP → VRPTW → EVRPTW).

**Challenges & blockers**
- Lin et al. (2021) does not release code; specific implementation details (graph embedding depth, exact masking boundary conditions, charging time modelling) must be inferred from the paper text.
- Need to obtain Schneider EVRPTW benchmark instances — not yet downloaded.

**Next steps**
- Download Schneider EVRPTW benchmark instances (`c101_21.txt` etc.) and place in `data/`.
- Begin implementing `EVRPTWEnv` in RL4CO: extend `VRPTWEnv` with battery state, charging station nodes, and masking logic.
- Run AM on CVRP (already done in smoke test) then on VRPTW (built-in RL4CO) as stepping stones.
- Decide on innovation direction (POMO augmentation vs. curriculum training) and document in `docs/`.

**Hours spent (optional):** ~10h

**Links (optional):**
- Reading notes: [`docs/reading_notes.md`](reading_notes.md)
- Reference handbook: [`docs/reference_handbook.md`](reference_handbook.md)
- Reading plan: [`docs/reading_plan.md`](reading_plan.md)

---

### Week 3 — 2026-06-30

**Attended this week's meeting:** Yes *(assumed; update if needed)*

**Progress this week**
- Focused on `labs/tasks/week02_works.md`, covering both **Step 1: POMO approach** and **Step 2: GA approach**.
- Cloned and inspected the original POMO repository in `labs/week2/pomo`, focusing on the updated Python implementation under `NEW_py_ver`.
- Ran POMO test scripts using the provided checkpoints in CPU debug mode:
- `POMO-TSP`, `TSP20`: NO-AUG score `3.8146`, AUG score `3.8139`, runtime `2.44 s`.
- `POMO-TSP`, `TSP100`: NO-AUG score `7.8014`, AUG score `7.7858`, runtime `22.41 s`.
- `POMO-CVRP`, `CVRP100`: NO-AUG score `15.6327`, AUG score `15.5858`, runtime `4.12 s`.
- Read through the cloned `labs/week2/ga_evrptw` codebase and clarified the role of its main concepts: `individual` (chromosome / customer ordering), `route` (decoded vehicle routes), `instance` (benchmark data dict), fitness, population, crossover, mutation, and penalty-based time-window handling.
- Confirmed that the reference GA solver targets **VRPTW**, not full EVRPTW: it does not yet model battery state or charging stations.
- Ran the two provided GA baseline experiments successfully:
- `sample_R101.py` on a 25-customer Solomon instance.
- `sample_C204.py` on a 100-customer Solomon instance.
- Recorded the main baseline outputs for Week 2 comparison:
- `R101`: total cost `7170.6752`, `5` vehicles, runtime `0.37 s`.
- `C204`: total cost `43059.6433`, `4` vehicles, runtime `14.06 s`.
- Created a Week 2 baseline comparison document in `docs/week02_method_comparison.md`, summarising POMO and GA results, constraint coverage, and limitations.

**Challenges & blockers**
- POMO-TSP and POMO-CVRP are useful learning-based baselines, but the original implementation does not include time windows, battery state, or charging stations.
- The cloned GA repository is a **VRPTW** solver only, so it cannot be used as an EVRPTW baseline without further modification.
- Time windows are handled mainly through waiting and delay penalties, rather than a stricter EV feasibility mechanism with battery and charging logic.
- The result values from POMO and GA are not directly comparable because they use different problem definitions and objective formulations.

**Next steps**
- Use the Week 2 comparison table to explain the difference between learning-based POMO and heuristic GA baselines.
- Decide whether to implement a minimal `battery` constraint next, likely by modifying `ind2route()` and/or `eval_vrptw()`.
- Identify which baseline is more suitable as the first extension target toward EVRP-TW: POMO-CVRP with added TW/E constraints, or GA-VRPTW with added battery constraints.
- Continue reporting objective value, feasibility status, constraint violations, and runtime together.

**Hours spent (optional):** ~9h

**Links (optional):**
- Week 2 task brief: [`labs/tasks/week02_works.md`](../labs/tasks/week02_works.md)
- Week 2 comparison: [`docs/week02_method_comparison.md`](week02_method_comparison.md)
- POMO baseline code: [`labs/week2/pomo/NEW_py_ver`](../labs/week2/pomo/NEW_py_ver)
- GA baseline code: [`labs/week2/ga_evrptw/gavrptw/core.py`](../labs/week2/ga_evrptw/gavrptw/core.py)
- GA sample runs: [`labs/week2/ga_evrptw/sample_R101.py`](../labs/week2/ga_evrptw/sample_R101.py), [`labs/week2/ga_evrptw/sample_C204.py`](../labs/week2/ga_evrptw/sample_C204.py)
- GA result logs: [`labs/week2/ga_evrptw/results/R101_uC8.0_iC60.0_wC0.5_dC1.5_iS25_pS80_cP0.85_mP0.01_nG100.csv`](../labs/week2/ga_evrptw/results/R101_uC8.0_iC60.0_wC0.5_dC1.5_iS25_pS80_cP0.85_mP0.01_nG100.csv), [`labs/week2/ga_evrptw/results/C204_uC8.0_iC100.0_wC1.0_dC1.5_iS100_pS400_cP0.85_mP0.02_nG300.csv`](../labs/week2/ga_evrptw/results/C204_uC8.0_iC100.0_wC1.0_dC1.5_iS100_pS400_cP0.85_mP0.02_nG300.csv)
