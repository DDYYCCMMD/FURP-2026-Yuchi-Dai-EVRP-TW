"""
Training script for EVRP-TW replication (Lin et al. 2021).

Usage:
    conda activate evrptw
    cd FURP-2026-Yuchi-Dai-EVRP-TW
    python src/train.py [--fast]

  --fast : small model + 5 epochs for quick smoke-test

Reference hyperparameters (Lin et al. 2021 / Kool 2019):
  embedding_dim = 128
  n_heads       = 8
  n_layers      = 3
  batch_size    = 512
  lr            = 1e-4
  n_epochs      = 100
  train_size    = 128_000  (instances per epoch)
"""

import sys
import os
import argparse
import torch
import lightning as L

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from rl4co.models import AttentionModel
from rl4co.utils import RL4COTrainer

from src.envs.evrptw_env import EVRPTWEnv
from src.models.evrptw_embeddings import EVRPTWInitEmbedding, EVRPTWContextEmbedding


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fast", action="store_true",
                        help="Quick smoke-test with tiny model and 5 epochs")
    parser.add_argument("--n_customer", type=int, default=20,
                        help="Number of customers (paper: 100)")
    parser.add_argument("--n_station", type=int, default=5,
                        help="Number of charging stations (paper: 21)")
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--batch_size", type=int, default=None)
    parser.add_argument("--embedding_dim", type=int, default=None)
    parser.add_argument("--device", type=str, default="auto")
    return parser.parse_args()


def main():
    args = parse_args()

    # ── Config ────────────────────────────────────────────────────────────────
    if args.fast:
        cfg = dict(
            n_customer    = 10,
            n_station     = 3,
            embedding_dim = 128,   # keep default; smaller dims cause encoder dim mismatch
            n_heads       = 8,
            n_layers      = 2,
            batch_size    = 32,
            train_size    = 320,
            val_size      = 64,
            lr            = 1e-3,
            n_epochs      = 3,
        )
        print("⚡ Fast mode: tiny model for smoke-test")
    else:
        cfg = dict(
            n_customer    = args.n_customer,
            n_station     = args.n_station,
            embedding_dim = args.embedding_dim or 128,
            n_heads       = 8,
            n_layers      = 3,
            batch_size    = args.batch_size or 512,
            train_size    = 128_000,
            val_size      = 10_000,
            lr            = 1e-4,
            n_epochs      = args.epochs or 100,
        )

    print(f"\n{'='*55}")
    print(f"  EVRP-TW Training — Lin et al. (2021) replication")
    print(f"  n_customer={cfg['n_customer']}  n_station={cfg['n_station']}")
    print(f"  embedding_dim={cfg['embedding_dim']}  heads={cfg['n_heads']}  layers={cfg['n_layers']}")
    print(f"  batch={cfg['batch_size']}  epochs={cfg['n_epochs']}")
    print(f"{'='*55}\n")

    # ── Environment ────────────────────────────────────────────────────────────
    env = EVRPTWEnv(
        n_customer=cfg["n_customer"],
        n_station =cfg["n_station"],
        generator_params=dict(
            n_customer=cfg["n_customer"],
            n_station =cfg["n_station"],
        ),
    )

    # ── Custom embeddings ──────────────────────────────────────────────────────
    init_embedding    = EVRPTWInitEmbedding(embedding_dim=cfg["embedding_dim"])
    context_embedding = EVRPTWContextEmbedding(embedding_dim=cfg["embedding_dim"])

    # ── Model ──────────────────────────────────────────────────────────────────
    # AttentionModel with REINFORCE + greedy rollout baseline (Kool 2019)
    model = AttentionModel(
        env,
        policy_kwargs=dict(
            init_embedding=init_embedding,
            context_embedding=context_embedding,
            num_heads=cfg["n_heads"],
            num_encoder_layers=cfg["n_layers"],
        ),
        baseline="rollout",
        train_data_size=cfg["train_size"],
        val_data_size=cfg["val_size"],
        batch_size=cfg["batch_size"],
        optimizer_kwargs={"lr": cfg["lr"]},
    )

    # ── Trainer ────────────────────────────────────────────────────────────────
    trainer = RL4COTrainer(
        max_epochs=cfg["n_epochs"],
        accelerator=args.device,            # "auto" → MPS on Apple Silicon
        devices=1,
        logger=True,                        # TensorBoard in lightning_logs/
        gradient_clip_val=1.0,             # recommended for REINFORCE
    )

    print("Starting training...")
    trainer.fit(model)

    # ── Save checkpoint ────────────────────────────────────────────────────────
    ckpt_dir = "results/checkpoints"
    os.makedirs(ckpt_dir, exist_ok=True)
    ckpt_path = f"{ckpt_dir}/evrptw_n{cfg['n_customer']}_s{cfg['n_station']}.ckpt"
    trainer.save_checkpoint(ckpt_path)
    print(f"\n✓ Checkpoint saved: {ckpt_path}")


if __name__ == "__main__":
    main()
