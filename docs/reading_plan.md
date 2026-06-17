# Reading Plan — EVRP-TW Literature

Target completion: **Week 2 (by 2026-06-21)**  
Goal: build the conceptual foundation needed to read and replicate Lin et al. (2021).

Track your progress by checking off each paper below.

---

## Reading depth guide

| Label | What it means |
|---|---|
| **Deep read** | Read every section; annotate model/method details and key results |
| **Focused read** | Read intro, method, experiments; skip proofs and appendices |
| **Skim** | Read abstract, intro, conclusion, and result tables only |

---

## Reading list (in order)

### 1. Solomon (1987) — VRPTW Benchmark ⬜
**Full title:** Algorithms for the Vehicle Routing and Scheduling Problems with Time Window Constraints  
**Journal:** Operations Research, 35(2), 254–265  
**DOI:** [10.1287/opre.35.2.254](https://doi.org/10.1287/opre.35.2.254)  
**Depth:** Skim  
**Why:** Defines the benchmark instances (C1, C2, R1, R2, RC1, RC2) used by almost every VRPTW and EVRPTW paper, including Lin et al. Understanding the instance structure is prerequisite to understanding any reported result.

---

### 2. Bräysy & Gendreau (2005) Part I — Classical VRPTW Heuristics ⬜
**Full title:** Vehicle Routing Problem with Time Windows, Part I: Route Construction and Local Search Algorithms  
**Journal:** Transportation Science, 39(1), 104–118  
**DOI:** [10.1287/trsc.1030.0056](https://doi.org/10.1287/trsc.1030.0056)  
**Depth:** Skim  
**Why:** Gives the standard performance reference for classical methods on Solomon instances. Read abstract + conclusion + result tables. Knowing typical solution quality gives you a baseline to compare your DRL results against. Do not read every algorithm in detail — that is not the focus of your project.

---

### 3. Schneider, Stenger & Goeke (2014) — EVRP-TW Core Definition ⬜
**Full title:** The Electric Vehicle-Routing Problem with Time Windows and Recharging Stations  
**Journal:** Transportation Science, 48(4), 500–520  
**DOI:** [10.1287/trsc.2013.0490](https://doi.org/10.1287/trsc.2013.0490)  
**Depth:** Deep read  
**Why:** This is the canonical formulation of EVRP-TW. Lin et al. (2021) builds directly on this problem definition. You must understand: vehicle capacity, battery capacity, time windows, recharging station visits, and the objective function. Also introduces the benchmark dataset used for EVRPTW evaluation.

---

### 4. Keskin & Çatay (2016) — Partial Recharge ⬜
**Full title:** Partial Recharge Strategies for the Electric Vehicle Routing Problem with Time Windows  
**Journal:** Transportation Research Part C, 65, 111–127  
**DOI:** [10.1016/j.trc.2016.01.013](https://doi.org/10.1016/j.trc.2016.01.013)  
**Depth:** Skim  
**Why:** Extends Schneider 2014 with partial recharging (vehicles don't need to charge to full). **Note: Lin et al. (2021) assumes full recharge.** Read this to understand the design space, but don't let it block progress. Useful context for potential innovation work later.

---

### 5. Vinyals, Fortunato & Jaitly (2015) — Pointer Networks ⬜
**Full title:** Pointer Networks  
**Venue:** NeurIPS 2015  
**arXiv:** [1506.03134](https://arxiv.org/abs/1506.03134)  
**Depth:** Focused read  
**Why:** Introduces the attention-based "pointer" mechanism for selecting from an input sequence — the direct architectural predecessor to the model in Lin et al. (2021). Pay attention to how the attention score is computed and how it produces a probability distribution over nodes.

---

### 6. Bello et al. (2016) — RL for TSP ⬜
**Full title:** Neural Combinatorial Optimization with Reinforcement Learning  
**Venue:** ICLR 2017 (arXiv 2016)  
**arXiv:** [1611.09940](https://arxiv.org/abs/1611.09940)  
**Depth:** Focused read  
**Why:** First paper to use REINFORCE to train a Pointer Network on TSP. Establishes the RL training paradigm (actor-critic / policy gradient) that all subsequent neural routing papers follow, including Lin et al.

---

### 7. Nazari et al. (2018) — RL for VRP ⬜
**Full title:** Reinforcement Learning for Solving the Vehicle Routing Problem  
**Venue:** NeurIPS 2018  
**arXiv:** [1802.04240](https://arxiv.org/abs/1802.04240)  
**Depth:** Focused read  
**Why:** Extends Bello et al. to multi-vehicle routing with capacity constraints. Replaces the LSTM encoder with element-wise embeddings, making it applicable to VRP. This is the direct precursor to Kool et al. (2019) and Lin et al. (2021).

---

### 8. Kool, van Hoof & Welling (2019) — Attention Model ⬜
**Full title:** Attention, Learn to Solve Routing Problems!  
**Venue:** ICLR 2019  
**arXiv:** [1803.08475](https://arxiv.org/abs/1803.08475)  
**Depth:** Deep read  
**Why:** Introduces the Attention Model (AM) — the direct backbone of Lin et al. (2021). You must understand: multi-head attention encoder, context embedding for the decoder, compatibility-based attention for node selection, and REINFORCE with rollout baseline. This paper is central to your replication.

---

### 9. Lin, Ghaddar & Nathwani (2021) — DRL for EVRP-TW ⬜  ← **Target paper**
**Full title:** Deep Reinforcement Learning for Electric Vehicle Routing Problem with Time Windows  
**Journal:** IEEE Transactions on Intelligent Transportation Systems  
**arXiv:** [2010.02068](https://arxiv.org/abs/2010.02068) | **DOI:** [10.1109/TITS.2021.3105232](https://doi.org/10.1109/TITS.2021.3105232)  
**Depth:** Deep read  
**Why:** This is the paper you are replicating. Read it multiple times. Focus on: how EVRPTW state is encoded (node features for customers vs. charging stations vs. depot), how the masking mechanism enforces battery and time-window feasibility, and the exact training setup (batch size, learning rate, number of epochs, instance sizes).

---

### 9.5. Berto et al. (2023) — RL4CO Framework ⬜
**Full title:** RL4CO: An Extensive Reinforcement Learning for Combinatorial Optimization Benchmark  
**arXiv:** [2306.17100](https://arxiv.org/abs/2306.17100)  
**Depth:** Focused read (+ skim the [documentation](https://rl4co.readthedocs.io/))  
**Why:** RL4CO is the framework you will use for implementation. Read this to understand how environments, models, and trainers are structured in the codebase. Knowing this before you write any code will save significant debugging time.

---

### 10. Kwon et al. (2020) — POMO ⬜
**Full title:** POMO: Policy Optimization with Multiple Optima for Reinforcement Learning  
**Venue:** NeurIPS 2020  
**arXiv:** [2010.16011](https://arxiv.org/abs/2010.16011)  
**Depth:** Focused read  
**Why:** POMO is currently one of the strongest DRL baselines for routing problems. Introduces symmetric data augmentation (N starting nodes) during inference to improve solution quality. Relevant for your innovation work — applying POMO-style augmentation to EVRPTW is one candidate for the ≥10% improvement.

---

## Suggested weekly split

| Days | Papers |
|---|---|
| Day 1–2 | #1 Solomon, #2 Bräysy & Gendreau (skim both) |
| Day 3–4 | #3 Schneider (deep), #4 Keskin (skim) |
| Day 5 | #5 Pointer Networks, #6 Bello et al. |
| Day 6 | #7 Nazari, #8 Kool et al. (deep) |
| Day 7 | #9 Lin et al. first read-through + #9.5 RL4CO |
| Ongoing | #10 POMO (can carry into Week 3) |

---

## Notes template (for each paper)

Copy this block into your reading notes file as you read each paper:

```
### [Author Year] [Short title]

**Core idea (1–2 sentences):**

**Architecture / method:**

**Key result (numbers):**

**What it contributes to my project:**

**Open questions / things to clarify:**
```

---

*References in BibTeX format: see [`resource/references.bib`](../resource/references.bib)*  
*PDF files: [`resource/papers/`](../resource/papers/)*
