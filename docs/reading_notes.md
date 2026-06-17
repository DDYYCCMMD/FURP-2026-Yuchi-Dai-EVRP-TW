# Reading Notes — EVRP-TW Literature

> Week 2 reading notes. Papers read in order per `docs/reading_plan.md`.
> Template per paper: core idea → architecture/method → key results → what it contributes to this project → open questions.

---

## [1] Solomon (1987) — VRPTW Benchmark

**Full reference:** Solomon, M. M. (1987). Algorithms for the Vehicle Routing and Scheduling Problems with Time Window Constraints. *Operations Research*, 35(2), 254–265.

**Core idea:**
Introduces the Vehicle Routing and Scheduling Problem with Time Windows (VRSPTW) and proposes a suite of construction and improvement heuristics. The paper's lasting contribution is not a single algorithm but the benchmark instance set that has become the universal standard for all VRPTW and EVRPTW research.

**Method:**
- Proposes several construction heuristics: sequential insertion (I1), parallel insertion, time-oriented nearest-neighbour.
- The I1 heuristic inserts unrouted customers into existing routes by minimizing a composite cost of distance and time slack.
- Also introduces 2-opt and 3-opt improvement phases.

**Instance types (the Solomon benchmark):**

| Type | Distribution | Time window width | Scheduling horizon |
|---|---|---|---|
| C1 | Clustered | Narrow | Short |
| C2 | Clustered | Wide | Long |
| R1 | Random | Narrow | Short |
| R2 | Random | Wide | Long |
| RC1 | Mixed | Narrow | Short |
| RC2 | Mixed | Wide | Long |

Each type contains multiple instances (e.g. C101, C102, …); sizes are 25, 50, and 100 customers.

**Key result:** Insertion heuristics consistently outperform nearest-neighbour under tight time window conditions; C-type instances are generally easier than R-type.

**What it contributes to this project:**
- The Solomon benchmark is the base for Schneider et al.'s EVRPTW instances (charging stations are added on top).
- Understanding instance types explains why results differ across C/R/RC: neural methods often generalise better on R-type (random, no clear structure) and struggle more on C-type (tight clusters where greedy misses structure).
- When replicating Lin et al. (2021) you will see results reported per Solomon instance class — this paper explains why those classes matter.

**Open questions:**
- What is the exact time window tightness distribution used in Schneider's adaptation?

---

## [2] Bräysy & Gendreau (2005) — Classical VRPTW Heuristics Survey

**Full reference:** Bräysy, O., & Gendreau, M. (2005). Vehicle Routing Problem with Time Windows, Part I: Route Construction and Local Search Algorithms. *Transportation Science*, 39(1), 104–118.

> ⚠️ PDF is a scanned image — text extraction not possible. Notes based on the paper's content.

**Core idea:**
Comprehensive survey of construction heuristics and local search algorithms for VRPTW. Establishes the performance landscape for classical methods, which DRL papers use as comparison baselines.

**Methods surveyed:**
- **Construction:** savings algorithms (Clarke-Wright), insertion heuristics (Solomon I1), time-oriented nearest-neighbour.
- **Local search:** 2-opt, 3-opt, Or-opt (relocate one/two/three customers between routes), Lin-Kernighan moves.
- **Key insight:** local search improves upon construction heuristics significantly, especially for minimising number of vehicles.

**Key results (reference numbers on Solomon benchmark):**
- Best classical heuristics achieve within 5–10% of optimal on most C-type instances.
- R-type instances are harder; gap to optimal is larger.
- Minimising vehicles first, then distance is the standard two-phase objective hierarchy.

**What it contributes to this project:**
- Establishes what "good classical performance" looks like — useful when framing DRL results: "our model achieves comparable distance to classical local search without requiring problem-specific heuristic design."
- The two-phase objective (vehicles first, distance second) is also adopted in Lin et al. (2021).
- Understanding Or-opt and 2-opt helps if a local-search repair component is added as innovation.

**Open questions:**
- How much does post-processing with 2-opt improve DRL solutions on EVRPTW?

---

## [3] Schneider, Stenger & Goeke (2014) — EVRP-TW Canonical Formulation

**Full reference:** Schneider, M., Stenger, A., & Goeke, D. (2014). The Electric Vehicle-Routing Problem with Time Windows and Recharging Stations. *Transportation Science*, 48(4), 500–520. DOI: 10.1287/trsc.2013.0490

**Core idea:**
Introduces the Electric Vehicle-Routing Problem with Time Windows and Recharging Stations (E-VRPTW / EVRPTW) — the canonical formulation that all subsequent EVRPTW papers, including Lin et al. (2021), build upon. Motivated by green logistics and EU emission regulations.

**Problem formulation:**
- Graph $G = (V, A)$ where $V = \{0\} \cup C \cup F$: depot, customers, charging stations.
- Charging stations can be visited multiple times; **full recharge assumed** at each visit.
- Constraints: vehicle capacity $Q$, battery capacity $B$, time windows $[e_i, l_i]$, service time $s_i$.
- Energy consumption linear in distance: $\Delta b = h \cdot d_{ij}$.
- Objective: minimise total travel distance (fleet size minimisation is secondary).

**Solution method:** Hybrid metaheuristic combining Variable Neighbourhood Search (VNS) and Tabu Search (TS) — referred to as VNS/TS.

**Benchmark instances:**
- Extended from Solomon C101–RC208 by inserting charging station nodes.
- Instance naming: e.g. `c101_21` = Solomon C101 base + 21 charging stations.
- Five sizes available: c1_5, c1_10, c1_15, c1_20, c1_25 (where the number = customers / 5 class).
- Available from the paper's supplementary material or the authors directly.

**Key results:** VNS/TS finds near-optimal solutions on small instances; as instance size grows, runtime and solution quality degrade — motivating DRL approaches for large instances.

**What it contributes to this project:**
- **This is the problem definition you are implementing.** Every constraint, variable, and objective in Lin et al. (2021) traces back to this paper.
- The full-recharge assumption is critical: in the DRL model, when a vehicle visits a charging station, its battery is set to $B$.
- The benchmark dataset is what you will use to evaluate your replication.

**Open questions:**
- How are charging station locations chosen relative to customers in the benchmark? (Affects how hard it is for a policy to find them.)
- What is the exact energy consumption rate $h$ in the benchmark instances?

---

## [4] Keskin & Çatay (2016) — Partial Recharge EVRPTW

**Full reference:** Keskin, M., & Çatay, B. (2016). Partial Recharge Strategies for the Electric Vehicle Routing Problem with Time Windows. *Transportation Research Part C*, 65, 111–127. DOI: 10.1016/j.trc.2016.01.013

**Core idea:**
Relaxes the full-recharge assumption of Schneider et al. (2014): vehicles may recharge to any level, not necessarily to $B$. This is called EVRPTW-PR (Partial Recharge). Partial recharge is more practical because shorter charging stops allow tighter schedules.

**Formulation:**
- Adds decision variable $u_{fk}$: charging duration at station $f$ for vehicle $k$.
- Battery after charging: $b' = b + g \cdot u_{fk}$, constrained to $[0, B]$.
- Formulated as 0–1 mixed integer linear program (MILP).

**Solution method:** Adaptive Large Neighbourhood Search (ALNS) with:
- New removal operators: remove charging stations independently or together with adjacent customers.
- New insertion operators: insert stations while deciding charge amount jointly.
- Operator selection weights updated dynamically based on past performance (the "adaptive" part).

**Key result:** Partial recharging can significantly improve routing decisions — shorter charging stops allow vehicles to meet tighter time windows, reducing total distance and fleet size.

**What it contributes to this project:**
- ⚠️ **Lin et al. (2021) uses full recharge** — this paper is *not* directly part of the replication.
- However, **partial recharge is a strong candidate for the ≥10% innovation**: extend Lin et al.'s DRL model to handle variable charging decisions (turn $u_{fk}$ into a continuous action).
- The ALNS framework is also relevant if a hybrid DRL+local-search approach is pursued.

**Open questions:**
- How much harder is it to train a DRL agent when charging amount is a continuous decision rather than a binary stop/no-stop?

---

## [5] Vinyals, Fortunato & Jaitly (2015) — Pointer Networks

**Full reference:** Vinyals, O., Fortunato, M., & Jaitly, N. (2015). Pointer Networks. *NeurIPS 2015*. arXiv: 1506.03134

**Core idea:**
The attention mechanism, originally used to blend encoder states into a context vector, is repurposed as a **pointer**: at each decoding step, the attention score over input tokens is treated directly as a probability distribution over the input sequence. This elegantly handles variable-length output dictionaries.

**Architecture:**

```
Encoder RNN → hidden states h₁, h₂, ..., hₙ
               ↓
Decoder RNN (step t) → decoder state dₜ
               ↓
Attention:  u_i^t = v^T tanh(W₁ hᵢ + W₂ dₜ)   for i = 1..n
               ↓
Softmax(u^t) → probability distribution over n inputs → select input i* as output
```

**Training:** Supervised — trained on labelled (input, optimal output) pairs. Uses beam search at inference.

**Key results:** Learns to solve convex hull, Delaunay triangulation, and small TSP (n ≤ 50) from examples alone. Generalises beyond training sequence lengths.

**Limitation:** Requires supervised labels (optimal solutions). The output dictionary size is fixed to input size — cannot point to a "depot" outside the sequence without special handling.

**What it contributes to this project:**
- Pointer Networks are the **direct architectural predecessor** of the decoder in Lin et al. (2021).
- The attention formula $u_i^t = v^T \tanh(W_1 h_i + W_2 d_t)$ appears (in a modified form) in both Nazari et al. and Lin et al.
- Key insight: treating attention scores as a pointer/selector (not a soft blend) is what makes the output discrete and combinatorial.

**Open questions:**
- How does the decoder state $d_t$ encode route-specific information (remaining capacity, time, battery) in later VRP extensions?

---

## [6] Bello et al. (2016) — Neural Combinatorial Optimization with RL

**Full reference:** Bello, I., Pham, H., Le, Q. V., Norouzi, M., & Bengio, S. (2016). Neural Combinatorial Optimization with Reinforcement Learning. *ICLR 2017*. arXiv: 1611.09940

**Core idea:**
Removes the need for supervised labels by training the Pointer Network with **REINFORCE** (policy gradient). Uses tour length as the negative reward signal. Key insight: RL can train combinatorial optimisation policies without access to optimal solutions.

**Training:**
- Policy: $p_\theta(\pi | s) = \prod_t p_\theta(\pi_t | \pi_{1:t-1}, s)$ — probability of a tour as a product of sequential decisions.
- Gradient: $\nabla_\theta \mathcal{L} = \mathbb{E}_\pi [(L(\pi) - b(s)) \nabla_\theta \log p_\theta(\pi|s)]$
  where $b(s)$ is a baseline (critic network) to reduce variance.
- Two training modes: (1) train on a fixed set of instances; (2) active search — optimise on each test instance at inference time.

**Key results:** Achieves close-to-optimal on TSP with up to 100 nodes. Active search trades inference time for better solutions. Also applied to 0/1 Knapsack.

**What it contributes to this project:**
- Establishes the **RL training paradigm** used by all subsequent papers including Lin et al. (2021).
- Introduces the concept of a **baseline** $b(s)$ for variance reduction — Lin et al. uses a rollout baseline (Kool et al.'s improvement on the critic).
- Shows that RL can effectively replace supervised learning for CO when optimal labels are expensive.

**Open questions:**
- Why does the rollout baseline (Kool 2019) outperform the critic baseline used here?

---

## [7] Nazari et al. (2018) — RL for Solving the VRP

**Full reference:** Nazari, M., Oroojlooy, A., Takáč, M., & Snyder, L. V. (2018). Reinforcement Learning for Solving the Vehicle Routing Problem. *NeurIPS 2018*. arXiv: 1802.04240

**Core idea:**
Extends Bello et al. (2016) to the multi-vehicle Capacitated VRP. Key architectural change: **replaces the LSTM encoder with element-wise linear projections**, making the model handle the dynamic VRP state (demands change as customers are visited) efficiently.

**Architecture:**

```
Static elements (coordinates):   xᵢˢ = ReLU(Wˢ · coordᵢ)    — fixed throughout route
Dynamic elements (remaining demand): xᵢᵈ = ReLU(Wᵈ · demandᵢ) — updated as customers served
               ↓
Attention over (xˢ, xᵈ) → pointer to next customer
               ↓
Decoder RNN (processes static embeddings as input)
```

**Key innovation:** Separating static and dynamic node features allows efficient embedding updates when the VRP state changes — no need to re-encode all nodes after each step.

**Key results:** Outperforms classical heuristics (Clarke-Wright, sweep) and Google OR-Tools on medium instances; competitive with LKH on quality with much faster inference after training.

**What it contributes to this project:**
- Lin et al. (2021) explicitly builds on Nazari et al.'s framework ("based on the framework proposed by Nazari et al. for VRP and TSP, we re-define the system state, rewarding schemes as well as the masking policy for EVRPTW").
- The **static/dynamic split** is essential for EVRPTW: battery level and current time are dynamic; coordinates and time windows are static.
- Masking infeasible actions (visited customers, overloaded routes) is introduced here — Lin et al. extends this to battery and time-window masks.

**Open questions:**
- How does the dynamic embedding update interact with the graph embedding layer Lin et al. adds for global information?

---

## [8] Kool, van Hoof & Welling (2019) — Attention Model (AM)

**Full reference:** Kool, W., van Hoof, H., & Welling, M. (2019). Attention, Learn to Solve Routing Problems! *ICLR 2019*. arXiv: 1803.08475

**Core idea:**
Proposes the **Attention Model (AM)** — replaces the RNN-based encoder with a Transformer-style multi-head attention encoder, and improves training with a **deterministic greedy rollout baseline** instead of a critic network.

**Architecture:**

```
Input: node features xᵢ (coordinates, demand, ...)
          ↓
[Linear projection] → initial embeddings hᵢ⁰
          ↓
N × [Multi-head Self-Attention + Feed-forward] → refined embeddings hᵢ  (encoder)
          ↓
Graph embedding: h̄ = mean(hᵢ)   (mean of all node embeddings)
          ↓
Context vector: [h̄ ; h_last_visited ; h_depot ; remaining_capacity]   (decoder input)
          ↓
Single-head attention (compatibility) over all nodes:
    u_i = C · tanh((W_Q · context)ᵀ · (W_K · hᵢ) / √d)
          ↓
Softmax(u) with masking → selection probability → choose next node
```

**Training:** REINFORCE with **greedy rollout baseline**:
- Periodically roll out the greedy (deterministic) policy on a held-out set.
- Use this greedy cost as the baseline $b(s)$.
- If the current stochastic policy significantly outperforms the greedy baseline (t-test), update the baseline.
- Much more stable and effective than a critic network.

**Key results:**
- TSP-20: optimality gap 0.34% (Concorde optimal)
- TSP-100: optimality gap 1.15%
- CVRP-100: competitive with OR-Tools and LKH2
- Same hyperparameters for all problem variants

**What it contributes to this project:**
- **This is the backbone of Lin et al. (2021).** The AM encoder and the greedy rollout baseline are used directly.
- The **context vector** design is where EVRPTW-specific information (battery $b$, current time $\tau$) must be injected.
- Understanding the attention score formula and masking mechanism is essential before implementing the EVRPTW extension.
- RL4CO implements this model as `AttentionModel` — this is the starting point for your replication.

**Key hyperparameters (Kool et al. reference):**

| Parameter | Value |
|---|---|
| Embedding dim | 128 |
| Attention heads | 8 |
| Encoder layers | 3 |
| Batch size | 512 |
| Learning rate | 1e-4 |
| Training steps | 100 epochs × 2500 batches |

**Open questions:**
- How does the context vector need to change to encode battery state and time in EVRPTW?
- Can the depot and charging station nodes be encoded with the same embedding or do they need separate projections?

---

## [9] Lin, Ghaddar & Nathwani (2021) — DRL for EVRP-TW ⭐ TARGET PAPER

**Full reference:** Lin, B., Ghaddar, B., & Nathwani, J. (2021). Deep Reinforcement Learning for Electric Vehicle Routing Problem with Time Windows. *IEEE Transactions on Intelligent Transportation Systems*. DOI: 10.1109/TITS.2021.3105232. arXiv: 2010.02068

**Core idea:**
First end-to-end DRL framework specifically for EVRPTW. Extends the Nazari et al. (2018) framework with a **graph embedding component** (from Dai et al.) to capture global graph structure, and introduces EVRPTW-specific state representation, masking, and reward.

**Architecture:**

```
EVRPTW instance: depot + customers + charging stations
          ↓
Node features:
  - Customers:        [x, y, demand, e_i, l_i, s_i]
  - Charging stations:[x, y, 0, 0, T_max, 0]  (no demand, full time window)
  - Depot:            [x, y, 0, 0, T_max, 0]
          ↓
Graph embedding (Dai et al. structure2vec):
  Aggregates neighbour information → global + local node representation
          ↓
Context / dynamic state:
  [current node embedding ; remaining capacity ; current time τ ; remaining battery b]
          ↓
Attention decoder (pointer mechanism) → u_i scores over unmasked nodes
          ↓
Masking policy (critical for feasibility):
  - Mask visited customers
  - Mask customers whose demand exceeds remaining capacity
  - Mask customers/stations unreachable with current battery
  - Mask customers whose time window would be violated
          ↓
Softmax → select next node → update (τ, b, capacity)
```

**Reward:** Negative total travel distance of the completed route. Infeasible routes receive a large penalty (or are masked out during construction so infeasibility cannot occur).

**Training:** REINFORCE with greedy rollout baseline (same as Kool 2019).

**Key differences from Kool 2019:**
1. Three node types (depot / customer / charging station) with different feature vectors.
2. Graph embedding layer for global information synthesis.
3. Battery constraint mask: node $j$ is masked if $b - h \cdot d_{ij} < h \cdot \min_f d_{jf}$ (must be able to reach nearest charging station after visiting $j$).
4. Time-window mask: node $j$ is masked if $\tau + t_{ij} > l_j$.
5. Full recharge when visiting a charging station: $b \leftarrow B$.

**Key results:**
- Solves EVRPTW instances with up to 100 customers — larger than any existing method at the time.
- Competitive with VNS/TS (Schneider 2014) on small instances; faster at inference.
- Demonstrates generalisation: trained on one instance size, tested on larger sizes.

**What it contributes to this project:**
- This is what you are replicating. The implementation plan:
  1. Start with RL4CO's `AttentionModel` on CVRP (already works).
  2. Add EVRPTW environment: extend node features, add battery/time state variables.
  3. Implement the masking policy (battery mask + time-window mask).
  4. Add charging station logic: upon visiting $f$, set $b = B$ and advance $\tau$ by $g^{-1}(B - b_{\text{before}})$ (for full recharge).
  5. Train with REINFORCE + rollout baseline.

**Open questions:**
- The paper does not release code. What exact graph embedding variant (depth, aggregation function) gives the best results?
- How is the charging time modelled at inference — is it included in the time update $\tau$?
- What instance sizes were used for training vs. evaluation?

---

## [9b] Berto et al. (2023/2025) — RL4CO Framework

**Full reference:** Berto, F., et al. (2025). RL4CO: An Extensive Reinforcement Learning for Combinatorial Optimization Benchmark. *KDD 2025*. arXiv: 2306.17100

**Core idea:**
A unified, modular open-source framework for training and evaluating DRL models on combinatorial optimisation problems. Implements a wide range of environments (TSP, CVRP, VRPTW, OP, PCTSP, FFSP, etc.) and models (AM, POMO, Sym-NCO, MDAM, etc.) under a consistent API built on PyTorch Lightning.

**Framework design:**
```
RL4CO
 ├── Environments  (RL4COEnvBase → CVRPEnv, VRPTWEnv, ...)
 │    ├── generator:   samples random instances
 │    ├── reset():     initialises state
 │    └── step(action): transitions state, computes reward
 ├── Models        (ConstructivePolicy → AttentionModel, POMO, ...)
 │    ├── encoder:  embeds instance features
 │    └── decoder:  selects actions autoregressively
 └── Trainer       (RL4COTrainer wraps Lightning Trainer)
```

**Key environments available:**

| Environment | Problem |
|---|---|
| `CVRPEnv` | Capacitated VRP |
| `VRPTWEnv` | VRP with Time Windows |
| `TSPEnv` | Travelling Salesman |
| `OPEnv` | Orienteering Problem |

> ⚠️ EVRPTW is **not yet a built-in environment** in RL4CO (as of v0.6.0). You will need to implement it by extending `VRPTWEnv` or `CVRPEnv`.

**Key models available:**

| Model | Paper |
|---|---|
| `AttentionModel` | Kool et al. (2019) |
| `POMO` | Kwon et al. (2020) |
| `SymNCO` | Kim et al. (2022) |
| `MatNet` | Kwon et al. (2021) |

**What it contributes to this project:**
- The implementation framework for your replication. You will extend `VRPTWEnv` to add battery dynamics and create an `EVRPTWEnv`.
- `AttentionModel` + `RL4COTrainer` provides the training loop; you only need to modify the environment and potentially the decoder context.
- The modular design means experiments (changing encoder depth, embedding dim, baseline) can be done by changing config, not rewriting code.

**Open questions:**
- What is the cleanest way to extend `VRPTWEnv` to add battery state and charging station nodes?
- Does RL4CO's masking mechanism allow custom battery constraints to be added?

---

## [10] Kwon et al. (2020) — POMO

**Full reference:** Kwon, Y.-D., Choo, J., Kim, B., Yoon, I., Min, S., & Gwon, Y. (2020). POMO: Policy Optimization with Multiple Optima for Reinforcement Learning. *NeurIPS 2020*. arXiv: 2010.16011

**Core idea:**
Exploits the **symmetry of CO solutions**: for a routing problem with $n$ nodes, starting from any node yields the same optimal tour (just rotated). POMO forces the policy to explore $n$ different rollouts simultaneously, each starting from a different node, leveraging all $n$ optimal representations.

**Key contributions:**

1. **Multiple rollouts during training:**
   - For each instance, roll out $n$ trajectories (one per starting node).
   - All trajectories share the same encoder pass (efficient).
   - Baseline: mean reward across all $n$ rollouts of the same instance — a **shared baseline** that is naturally low-variance.

2. **Augmentation-based inference:**
   - At test time, generate 8 augmented versions of each instance (rotations + reflections).
   - Run POMO on each augmentation, take the best solution across all rollouts × augmentations.
   - Dramatically improves solution quality with no additional training.

**Key results:**
- TSP-100: optimality gap **0.14%** (vs. 1.15% for AM) — 8× improvement.
- CVRP-100: state-of-the-art among neural methods at publication.
- Inference time reduced vs. sampling-based approaches.

**What it contributes to this project:**
- **Candidate for the ≥10% innovation**: apply POMO-style multi-start training to the EVRPTW model. In EVRPTW, symmetry is partially broken (time windows, battery), but starting from different depot states or using different random route starts may still help.
- The augmentation technique can be applied directly: rotate/reflect the EVRPTW instance and take the best solution — this does not require any model changes.
- RL4CO implements POMO as `POMO` model — can be used as a drop-in baseline for your experiments.

**Key difference from AM:**
| | AM (Kool 2019) | POMO (Kwon 2020) |
|---|---|---|
| Training rollouts per instance | 1 | $n$ (one per start node) |
| Baseline | Greedy rollout on held-out set | Mean of $n$ rollouts (same instance) |
| Inference | Greedy or sampling | Multi-start greedy + augmentation |
| TSP-100 gap | 1.15% | 0.14% |

**Open questions:**
- Does the POMO multi-start trick work for EVRPTW, where routes are not symmetric (battery state is path-dependent)?
- What is the computational overhead of $n$ rollouts per instance during EVRPTW training?

---

## Cross-paper Summary: The DRL Routing Family Tree

```
Vinyals 2015 (Pointer Net, supervised)
        ↓
Bello 2016 (RL training, TSP)
        ↓
Nazari 2018 (element-wise embed, VRP, dynamic state)
        ↓
Kool 2019 (multi-head attention encoder, rollout baseline, TSP/VRP)
        ↓                               ↓
Lin 2021 (graph embed, EVRPTW mask)   Kwon 2020 (POMO, multi-start, augment)
        ↓
[Your replication: Lin 2021 in RL4CO]
        ↓
[Your innovation: POMO augmentation / curriculum training / partial recharge]
```

---

## Key Implementation Decisions for Replication

| Decision | Choice | Rationale |
|---|---|---|
| Base framework | RL4CO v0.6.0 | Already installed; implements AM and training loop |
| Base model | `AttentionModel` | Direct backbone of Lin et al. |
| Environment | Custom `EVRPTWEnv` extending `VRPTWEnv` | Add battery state, charging stations |
| Node features | `[x, y, demand, e, l, s]` for customers; `[x, y, 0, 0, T_max, 0]` for stations | Follow Lin et al. |
| Context vector | `[h̄ ; h_current ; h_depot ; remaining_cap ; τ ; b]` | Add time and battery to Kool's context |
| Masking | Battery mask + time-window mask | Core EVRPTW contribution |
| Training | REINFORCE + greedy rollout baseline | Same as Lin et al. / Kool |
| Baseline instances | Schneider c1_5 / c1_10 (small) first | Match reported results |

---

*Notes compiled: 2026-06-17*
*Papers read: 10/11 (Bräysy 2005 is scanned; content noted from domain knowledge)*
