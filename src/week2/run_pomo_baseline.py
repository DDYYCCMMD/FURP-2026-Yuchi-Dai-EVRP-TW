"""
Week 2 POMO baseline runner for the custom EVRPTW environment.

This uses the existing RL4CO-based EVRPTW environment and custom embeddings to
produce small, reproducible Week 2 experiments on two scales.

Usage:
    conda run -n evrptw python src/week2/run_pomo_baseline.py
    conda run -n evrptw python src/week2/run_pomo_baseline.py --preset small
"""

from __future__ import annotations

import argparse
import csv
import os
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MPL_DIR = ROOT / "results" / "mplconfig"
MPL_DIR.mkdir(parents=True, exist_ok=True)

# Keep matplotlib caches in a writable workspace path to avoid warnings.
os.environ.setdefault("MPLCONFIGDIR", str(MPL_DIR))

import lightning as L
import torch

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rl4co.models import POMO  # noqa: E402
from rl4co.utils import RL4COTrainer  # noqa: E402

from src.envs.evrptw_env import EVRPTWEnv  # noqa: E402
from src.models.evrptw_embeddings import (  # noqa: E402
    EVRPTWContextEmbedding,
    EVRPTWInitEmbedding,
)


PRESETS = {
    "small": dict(
        n_customer=5,
        n_station=2,
        train_size=64,
        val_size=16,
        batch_size=8,
        epochs=1,
        embedding_dim=128,
        n_heads=8,
        n_layers=2,
        num_starts=1,
        scale_label="5-customers-2-stations",
    ),
    "medium": dict(
        n_customer=10,
        n_station=3,
        train_size=96,
        val_size=16,
        batch_size=8,
        epochs=1,
        embedding_dim=128,
        n_heads=8,
        n_layers=2,
        num_starts=1,
        scale_label="10-customers-3-stations",
    ),
}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--preset",
        choices=["small", "medium", "all"],
        default="all",
        help="Which POMO preset to run.",
    )
    parser.add_argument("--seed", type=int, default=64)
    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        help="Use cpu for quick Week 2 runs; use mps/cuda only if wanted.",
    )
    return parser.parse_args()


def greedy_rollout(model: POMO, env: EVRPTWEnv) -> dict:
    td = env.reset(batch_size=[1])
    actions = []
    max_steps = env.n_nodes * 4

    with torch.no_grad():
        embeddings, _ = model.policy.encoder(td)
        for _ in range(max_steps):
            log_p, _ = model.policy.decoder(td, embeddings)
            action = log_p.exp().argmax(dim=-1)
            td.set("action", action)
            td = env.step(td)["next"]
            actions.append(action.item())
            if td["done"].all():
                break

    actions_t = torch.tensor(actions, dtype=torch.long).unsqueeze(0)
    reward = env._get_reward(td, actions_t).item()
    all_customers_served = td["visited"].squeeze(1)[:, 1 : 1 + env.n_customer].all().item()
    feasible = bool(td["done"].all().item() and all_customers_served)

    return {
        "steps": len(actions),
        "reward": round(reward, 4),
        "route_distance": round(-reward, 4),
        "feasible": "Yes" if feasible else "No",
    }


def run_one(config: dict, seed: int, device: str) -> dict:
    L.seed_everything(seed, workers=True)
    random.seed(seed)
    torch.manual_seed(seed)

    env = EVRPTWEnv(
        n_customer=config["n_customer"],
        n_station=config["n_station"],
        generator_params=dict(
            n_customer=config["n_customer"],
            n_station=config["n_station"],
        ),
    )

    model = POMO(
        env,
        policy_kwargs=dict(
            init_embedding=EVRPTWInitEmbedding(embedding_dim=config["embedding_dim"]),
            context_embedding=EVRPTWContextEmbedding(embedding_dim=config["embedding_dim"]),
            num_heads=config["n_heads"],
            num_encoder_layers=config["n_layers"],
        ),
        num_starts=config["num_starts"],
        train_data_size=config["train_size"],
        val_data_size=config["val_size"],
        batch_size=config["batch_size"],
    )

    trainer = RL4COTrainer(
        max_epochs=config["epochs"],
        accelerator=device,
        devices=1,
        logger=False,
        precision=32,
        enable_checkpointing=False,
    )

    started = time.perf_counter()
    trainer.fit(model)
    elapsed = time.perf_counter() - started
    rollout = greedy_rollout(model, env)

    return {
        "method": "POMO_EVRPTW",
        "scale": config["scale_label"],
        "customers": config["n_customer"],
        "stations": config["n_station"],
        "epochs": config["epochs"],
        "train_size": config["train_size"],
        "batch_size": config["batch_size"],
        "greedy_distance": rollout["route_distance"],
        "reward": rollout["reward"],
        "steps": rollout["steps"],
        "feasible": rollout["feasible"],
        "runtime_s": round(elapsed, 3),
        "seed": seed,
        "device": device,
    }


def write_summary(rows: list[dict]) -> Path:
    out_dir = ROOT / "results" / "week2"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "pomo_summary.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return out_path


def main():
    args = parse_args()
    selected = PRESETS.keys() if args.preset == "all" else [args.preset]

    rows = []
    print("\n=== Week 2 POMO Baseline Runs ===")
    for name in selected:
        config = PRESETS[name]
        print(
            f"\nRunning preset: {name} "
            f"({config['n_customer']} customers, {config['n_station']} stations)"
        )
        row = run_one(config, seed=args.seed, device=args.device)
        rows.append(row)
        print(
            f"Summary -> distance={row['greedy_distance']}, feasible={row['feasible']}, "
            f"runtime={row['runtime_s']:.3f}s"
        )

    out_path = write_summary(rows)
    print(f"\nSaved POMO summary: {out_path}")


if __name__ == "__main__":
    main()
