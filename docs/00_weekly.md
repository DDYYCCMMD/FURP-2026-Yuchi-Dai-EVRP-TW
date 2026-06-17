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
