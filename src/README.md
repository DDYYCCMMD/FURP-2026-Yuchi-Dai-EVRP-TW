# `/src` — EVRP-TW Replication & Experiments

Replication of **Lin, Ghaddar & Nathwani (2021)**,  
*"Deep Reinforcement Learning for Electric Vehicle Routing Problem with Time Windows"*,  
IEEE Transactions on Intelligent Transportation Systems.  
arXiv: [2010.02068](https://arxiv.org/abs/2010.02068) | DOI: [10.1109/TITS.2021.3105232](https://doi.org/10.1109/TITS.2021.3105232)

---

## Directory layout

```
/src
 ├── README.md            ← this file
 ├── data/                ← benchmark instances (Solomon VRPTW, Schneider EVRPTW)
 ├── experiments/         ← training scripts, notebooks, configs
 └── results/             ← logs, figures, metric tables
```

---

## Environment setup (macOS)

### Prerequisites

- macOS 12+ (Apple Silicon or Intel both supported)
- [Homebrew](https://brew.sh/) installed
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Miniforge](https://github.com/conda-forge/miniforge) installed

### Step 1 — create conda environment

```bash
conda create -n evrptw python=3.11 -y
conda activate evrptw
```

### Step 2 — install PyTorch

**Apple Silicon (M1/M2/M3):**
```bash
pip install torch torchvision torchaudio
```

**Intel Mac:**
```bash
pip install torch torchvision torchaudio
```

Verify:
```bash
python -c "import torch; print(torch.__version__); print(torch.backends.mps.is_available())"
```

### Step 3 — install RL4CO

[RL4CO](https://github.com/ai4co/rl4co) provides the Attention Model and POMO baselines used in this project.

```bash
pip install rl4co
```

Verify:
```bash
python -c "import rl4co; print(rl4co.__version__)"
```

### Step 4 — install PyVRP (classical baseline)

[PyVRP](https://github.com/PyVRP/PyVRP) is used as the classical heuristic baseline for comparison.

```bash
pip install pyvrp
```

Verify:
```bash
python -c "import pyvrp; print(pyvrp.__version__)"
```

### Step 5 — install remaining dependencies

```bash
pip install numpy pandas matplotlib scipy tensorboard jupyter
```

---

## Smoke tests

Run these after setup to confirm the pipeline works end-to-end.

### 1. RL4CO — CVRP training smoke test

```bash
python - <<'EOF'
from rl4co.envs import CVRPEnv
from rl4co.models import AttentionModel
from rl4co.utils import RL4COTrainer
import lightning as L

env = CVRPEnv(generator_params=dict(num_loc=20))
model = AttentionModel(env, baseline="rollout", train_data_size=128, val_data_size=32)
trainer = L.Trainer(max_epochs=1, accelerator="auto")
trainer.fit(model)
print("RL4CO smoke test PASSED")
EOF
```

### 2. PyVRP — VRPTW small instance smoke test

```bash
python - <<'EOF'
from pyvrp import Model
from pyvrp.stop import MaxIterations

m = Model()
m.add_vehicle_type(capacity=10)
depot = m.add_depot(x=0, y=0)
clients = [
    m.add_client(x=1, y=2, delivery=2, tw_early=0, tw_late=50),
    m.add_client(x=3, y=1, delivery=3, tw_early=0, tw_late=50),
    m.add_client(x=2, y=4, delivery=1, tw_early=0, tw_late=50),
]
for frm in [depot] + clients:
    for to in [depot] + clients:
        if frm != to:
            dist = int(((frm.x - to.x)**2 + (frm.y - to.y)**2)**0.5 * 100)
            m.add_edge(frm, to, distance=dist, duration=dist)
res = m.solve(stop=MaxIterations(100), seed=42)
print(f"PyVRP smoke test PASSED — cost: {res.cost():.1f}, feasible: {res.is_feasible()}")
EOF
```

Both tests should complete without errors. If MPS (Apple Silicon GPU) is available, RL4CO will use it automatically.

---

## Data

Benchmark instances used in Lin et al. (2021):

| Dataset | Source | Notes |
|---|---|---|
| Solomon VRPTW | [Solomon (1987)](http://www.vrptw.org/) | Standard VRPTW benchmark, 25/50/100 customers |
| Schneider EVRPTW | [Schneider et al. (2014)](https://doi.org/10.1287/trsc.2013.0490) | Extends Solomon with charging stations and battery constraints |

Download links will be added here once data is confirmed.

---

## Replication plan

1. **Week 2** — Read Lin et al. (2021) in full; annotate architecture, loss, training details
2. **Week 3** — Implement / adapt Attention Model for EVRPTW in RL4CO; reproduce reported metrics on small instances
3. **Week 4** — Add full EVRPTW constraint handling (time windows + battery + charging); evaluate on Schneider benchmark
4. **Weeks 5–7** — Innovation: e.g. curriculum-based training, POMO augmentation, or local-search repair
5. **Week 8** — Final evaluation, ablation study, report

---

## Key references

- Lin, B., Ghaddar, B., & Nathwani, J. (2021). Deep reinforcement learning for electric vehicle routing problem with time windows. *IEEE TITS*. [arXiv 2010.02068](https://arxiv.org/abs/2010.02068)
- Berto, F., et al. (2023). RL4CO: An extensive reinforcement learning for combinatorial optimization benchmark. [arXiv 2306.17100](https://arxiv.org/abs/2306.17100)
- Schneider, M., Stenger, A., & Goeke, D. (2014). The electric vehicle-routing problem with time windows and recharging stations. *Transportation Science*. [DOI 10.1287/trsc.2013.0490](https://doi.org/10.1287/trsc.2013.0490)
