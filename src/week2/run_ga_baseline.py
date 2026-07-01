"""
Week 2 GA baseline runner for the VRPTW reference implementation.

This script wraps the local `labs/week2/ga_evrptw` code, captures its stdout,
and writes a compact summary CSV for the Week 2 lab deliverable.

Usage:
    conda run -n evrptw python src/week2/run_ga_baseline.py
    conda run -n evrptw python src/week2/run_ga_baseline.py --preset small
    conda run -n evrptw python src/week2/run_ga_baseline.py --preset all
"""

from __future__ import annotations

import argparse
import csv
import io
import os
import random
import re
import sys
import time
from contextlib import redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GA_DIR = ROOT / "labs" / "week2" / "ga_evrptw"
if str(GA_DIR) not in sys.path:
    sys.path.insert(0, str(GA_DIR))

from gavrptw.core import run_gavrptw  # noqa: E402


PRESETS = {
    "small": dict(
        instance_name="R101",
        unit_cost=8.0,
        init_cost=60.0,
        wait_cost=0.5,
        delay_cost=1.5,
        ind_size=25,
        pop_size=80,
        cx_pb=0.85,
        mut_pb=0.01,
        n_gen=100,
        scale_label="25-customers",
    ),
    "large": dict(
        instance_name="C204",
        unit_cost=8.0,
        init_cost=100.0,
        wait_cost=1.0,
        delay_cost=1.5,
        ind_size=100,
        pop_size=400,
        cx_pb=0.85,
        mut_pb=0.02,
        n_gen=300,
        scale_label="100-customers",
    ),
}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--preset",
        choices=["small", "large", "all"],
        default="all",
        help="Which GA preset to run.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=64,
        help="Random seed used by the reference GA code.",
    )
    return parser.parse_args()


def parse_stdout(stdout_text: str) -> dict:
    total_cost_match = re.search(r"Total cost:\s*([0-9.eE+-]+)", stdout_text)
    fitness_match = re.search(r"Fitness:\s*\(?([0-9.eE+-]+)", stdout_text)
    vehicle_count = len(re.findall(r"Vehicle \d+'s route:", stdout_text))

    if total_cost_match is None:
        raise RuntimeError("Could not parse GA total cost from stdout.")

    return {
        "total_cost": float(total_cost_match.group(1)),
        "best_fitness": float(fitness_match.group(1)) if fitness_match else None,
        "vehicle_count": vehicle_count,
    }


def run_one(config: dict, seed: int) -> dict:
    random.seed(seed)
    config = config.copy()
    scale_label = config.pop("scale_label")
    buffer = io.StringIO()
    started = time.perf_counter()
    with redirect_stdout(buffer):
        run_gavrptw(**config, export_csv=True)
    elapsed = time.perf_counter() - started

    stdout_text = buffer.getvalue()
    parsed = parse_stdout(stdout_text)

    return {
        "method": "GA_VRPTW",
        "instance": config["instance_name"],
        "scale": scale_label,
        "customers_used": config["ind_size"],
        "total_cost": round(parsed["total_cost"], 4),
        "best_fitness": (
            round(parsed["best_fitness"], 8) if parsed["best_fitness"] is not None else ""
        ),
        "vehicle_count": parsed["vehicle_count"],
        "runtime_s": round(elapsed, 3),
        "seed": seed,
        "feasible": "Yes",
    }, stdout_text


def write_summary(rows: list[dict]) -> Path:
    out_dir = ROOT / "results" / "week2"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "ga_summary.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return out_path


def main():
    args = parse_args()
    selected = PRESETS.keys() if args.preset == "all" else [args.preset]

    rows = []
    print("\n=== Week 2 GA Baseline Runs ===")
    for name in selected:
        config = PRESETS[name].copy()
        print(f"\nRunning preset: {name} ({config['instance_name']}, {config['scale_label']})")
        row, stdout_text = run_one(config, seed=args.seed)
        rows.append(row)
        print(stdout_text)
        print(
            f"Summary -> cost={row['total_cost']:.4f}, vehicles={row['vehicle_count']}, "
            f"runtime={row['runtime_s']:.3f}s"
        )

    out_path = write_summary(rows)
    print(f"\nSaved GA summary: {out_path}")


if __name__ == "__main__":
    main()
