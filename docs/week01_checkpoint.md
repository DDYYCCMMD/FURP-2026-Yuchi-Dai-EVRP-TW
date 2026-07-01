# Week 1 Checkpoint

## Team info

- Team name: EVRP-TW Deep RL (Individual)
- Members: Yuchi Dai
- Date: 2026-06-17

---

## Environment

- [x] Environment created — `conda create -n evrptw python=3.11`
- [x] Dependencies installed

| Package | Version |
|---|---|
| Python | 3.11.15 |
| PyTorch | 2.12.0 (MPS / Apple Silicon) |
| RL4CO | 0.6.0 |
| PyVRP | installed |
| NumPy | 2.4.6 |
| Matplotlib | 3.11.0 |
| Lightning | 2.6.5 |
| pandas | 3.0.3 |
| TensorBoard | 2.20.0 |

- [x] Repo structure understood — mandatory structure in place: `/docs`, `/src`, `/resource`, `/checklists`

---

## Baseline run

### RL4CO — CVRP smoke test

- [x] Baseline command executed

```bash
conda activate evrptw
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

- [x] Baseline command executed — training completed 1 epoch, `lightning_logs/` generated
- [x] Feasibility status reported — model trained without errors, MPS (Apple Silicon GPU) used
- [x] Evidence attached — `lightning_logs/` directory present in project root

### PyVRP — VRPTW smoke test

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

- [x] Baseline command executed — VRPTW 3-client instance solved
- [x] Objective value reported — cost reported by PyVRP solver
- [x] Feasibility status reported — `feasible: True`
- [x] Evidence attached — terminal output confirmed

---

## Reflection

1. **Main setup issue:** `pandas` and `tensorboard` were not installed by default when creating the conda environment.
2. **How it was solved:** Ran `pip install pandas tensorboard` inside the activated `evrptw` environment.
3. **Current risk for Week 2:** Reading 11 papers in one week is ambitious — priority will be Schneider 2014 and Kool 2019 first, as they are prerequisites for understanding Lin et al. (2021).
