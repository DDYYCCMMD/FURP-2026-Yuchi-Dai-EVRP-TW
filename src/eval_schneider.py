"""
Evaluate a trained EVRP-TW model on Schneider benchmark instances.

Usage:
    conda activate evrptw
    cd FURP-2026-Yuchi-Dai-EVRP-TW
    python src/eval_schneider.py --checkpoint results/checkpoints/evrptw_n100_s21.ckpt

Output:
    Prints a table: instance | distance | feasible | n_vehicles | time(s)
    Saves results/eval_schneider.csv

Evaluation protocol (Lin et al. 2021):
  - Greedy decoding (argmax at each step)
  - Infeasible = time-window or battery violation detected
  - Reports total travel distance for feasible solutions
"""

import sys
import os
import argparse
import time
import csv
import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from rl4co.models import AttentionModel

from labs.week6.src.envs.evrptw_env import EVRPTWEnv, CUSTOMER
from labs.week6.src.models.evrptw_embeddings import EVRPTWInitEmbedding, EVRPTWContextEmbedding
from labs.week6.src.data.schneider_loader import load_folder, check_instance


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--checkpoint", type=str, required=True,
                   help="Path to .ckpt saved by train.py")
    p.add_argument("--data_dir", type=str,
                   default="data/schneider_instances",
                   help="Folder with Schneider .txt files")
    p.add_argument("--n_customer", type=int, default=100)
    p.add_argument("--n_station",  type=int, default=21)
    p.add_argument("--embedding_dim", type=int, default=128)
    p.add_argument("--n_heads",   type=int, default=8)
    p.add_argument("--n_layers",  type=int, default=3)
    p.add_argument("--device",    type=str, default="cpu",
                   help="cpu | mps | cuda")
    return p.parse_args()


def greedy_rollout(model, env, td, device):
    """
    Run greedy (argmax) decoding from a reset state.
    Returns (actions [1, T], tour_length scalar).
    """
    td = td.to(device)
    td = env.reset(td=td, batch_size=[1])

    actions = []
    max_steps = env.n_nodes * 3   # safety limit

    with torch.no_grad():
        # Encode once
        embeddings, _ = model.policy.encoder(td)

        for _ in range(max_steps):
            # Decode one step
            log_p, _ = model.policy.decoder(td, embeddings)
            # Greedy: pick highest probability node
            action = log_p.exp().argmax(dim=-1)   # [1]
            td.set("action", action)
            td = env.step(td)["next"]
            actions.append(action.item())

            if td["done"].all():
                break

    actions_t = torch.tensor(actions, dtype=torch.long).unsqueeze(0)  # [1, T]

    # Compute tour length
    locs = td["locs"][0].cpu()
    depot_loc = locs[0]
    tour = [0] + actions + [0]
    total_dist = 0.0
    for i in range(len(tour) - 1):
        total_dist += torch.norm(locs[tour[i+1]] - locs[tour[i]]).item()

    return actions, total_dist


def check_feasibility(td_reset, actions, env):
    """
    Verify time-window and battery feasibility of a tour.
    Returns (feasible: bool, n_vehicles: int, violations: list).
    """
    locs         = td_reset["locs"][0]
    time_windows = td_reset["time_windows"][0]
    service_time = td_reset["service_time"][0]
    node_type    = td_reset["node_type"][0]

    battery      = 1.0
    current_time = 0.0
    n_vehicles   = 1
    violations   = []
    current_node = 0   # start at depot

    for step, nxt in enumerate(actions):
        dist = torch.norm(locs[nxt] - locs[current_node]).item()
        battery      -= dist
        current_time += dist

        # Wait if early
        tw_e = time_windows[nxt, 0].item()
        tw_l = time_windows[nxt, 1].item()
        if current_time < tw_e:
            current_time = tw_e

        # Check time window
        if current_time > tw_l + 1e-6:
            violations.append(f"TW violation at node {nxt} step {step}: "
                               f"arrival={current_time:.3f} > late={tw_l:.3f}")

        # Check battery
        if battery < -1e-6:
            violations.append(f"Battery violation at node {nxt} step {step}: "
                               f"battery={battery:.3f}")

        ntype = node_type[nxt].item()
        if ntype == 2:   # charging station → recharge
            charge_time = (1.0 - battery) * 3.39
            current_time += charge_time
            battery = 1.0
        elif ntype == 1:   # customer → add service time
            current_time += service_time[nxt].item()
        elif ntype == 0 and current_node != 0:   # returning to depot
            battery = 1.0
            n_vehicles += 1

        current_node = nxt

    feasible = len(violations) == 0
    return feasible, n_vehicles - 1, violations


def main():
    args = parse_args()
    device = torch.device(args.device)

    # ── Build model skeleton (same architecture as training) ─────────────────
    env = EVRPTWEnv(n_customer=args.n_customer, n_station=args.n_station)
    init_embedding    = EVRPTWInitEmbedding(embedding_dim=args.embedding_dim)
    context_embedding = EVRPTWContextEmbedding(embedding_dim=args.embedding_dim)

    model = AttentionModel.load_from_checkpoint(
        args.checkpoint,
        env=env,
        policy_kwargs=dict(
            init_embedding=init_embedding,
            context_embedding=context_embedding,
            embedding_dim=args.embedding_dim,
            num_heads=args.n_heads,
            num_encoder_layers=args.n_layers,
        ),
    )
    model.eval().to(device)

    # ── Load Schneider instances ─────────────────────────────────────────────
    instances = load_folder(args.data_dir)
    print(f"\nEvaluating {len(instances)} instances...\n")

    # Header
    print(f"{'Instance':<15} {'Distance':>10} {'Feasible':>9} {'Vehicles':>9} {'Time(s)':>8}")
    print("-" * 56)

    results = []
    n_feasible = 0

    for name, td in sorted(instances.items()):
        t0 = time.time()
        try:
            actions, dist = greedy_rollout(model, env, td, device)
            feasible, n_veh, viols = check_feasibility(td, actions, env)
            elapsed = time.time() - t0

            feas_str = "✓" if feasible else f"✗({len(viols)})"
            print(f"{name:<15} {dist:>10.3f} {feas_str:>9} {n_veh:>9} {elapsed:>8.2f}")

            if feasible:
                n_feasible += 1
            results.append({
                "instance":  name,
                "distance":  round(dist, 4),
                "feasible":  feasible,
                "n_vehicles": n_veh,
                "time_s":    round(elapsed, 3),
            })
        except Exception as e:
            print(f"{name:<15} ERROR: {e}")

    # ── Summary ─────────────────────────────────────────────────────────────
    n = len(results)
    feasible_dists = [r["distance"] for r in results if r["feasible"]]
    print("\n" + "=" * 56)
    print(f"Feasibility rate : {n_feasible}/{n} = {100*n_feasible/max(n,1):.1f}%")
    if feasible_dists:
        avg = sum(feasible_dists) / len(feasible_dists)
        print(f"Avg distance     : {avg:.3f}  (feasible instances only)")
    print("=" * 56)

    # ── Save CSV ─────────────────────────────────────────────────────────────
    os.makedirs("results", exist_ok=True)
    csv_path = "results/eval_schneider.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"\nResults saved: {csv_path}")


if __name__ == "__main__":
    main()
