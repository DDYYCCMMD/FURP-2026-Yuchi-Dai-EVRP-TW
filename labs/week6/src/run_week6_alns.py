"""CLI for the Week 6 full-recharge ALNS experiments.

Examples
--------
Check benchmark/configuration only:
    python -m labs.week6.src.run_week6_alns --check-config

Run the EVRPTW vertical slice:
    python -m labs.week6.src.run_week6_alns --mode evrptw

Run the time-window/capacity ablation on the same customer data:
    python -m labs.week6.src.run_week6_alns --mode vrptw
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, replace
from pathlib import Path

from labs.week6.src.alns.alns_solver import ALNSResult, solve
from labs.week6.src.alns.config import DEFAULT_CONFIG, Week6Config
from labs.week6.src.alns.instance_loader import load_schneider_instance


def parse_args() -> argparse.Namespace:
    defaults = DEFAULT_CONFIG.experiment
    parser = argparse.ArgumentParser(
        description="Run Week 6 ALNS on Schneider EVRPTW instances."
    )
    parser.add_argument(
        "--mode",
        choices=("evrptw", "vrptw"),
        default="evrptw",
        help="Enable or ablate battery constraints and charging repair.",
    )
    parser.add_argument(
        "--instances",
        nargs="+",
        default=list(defaults.instance_names),
        help="Instance stems under data/schneider_instances.",
    )
    parser.add_argument(
        "--seeds",
        nargs="+",
        type=int,
        default=list(defaults.seeds),
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=defaults.iterations,
    )
    parser.add_argument(
        "--time-limit",
        type=float,
        default=defaults.time_limit_s,
        help=(
            "Optional per-run wall-clock limit in seconds; the default and "
            "value 0 both mean no limit."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=defaults.output_dir,
    )
    parser.add_argument(
        "--local-search-probability",
        type=float,
        default=DEFAULT_CONFIG.operators.local_search_probability,
    )
    parser.add_argument("--disable-sa", action="store_true")
    parser.add_argument("--disable-adaptive", action="store_true")
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="Validate configuration and instance parsing, then exit.",
    )
    return parser.parse_args()


def build_config(args: argparse.Namespace) -> Week6Config:
    instance_names = tuple(Path(name).stem for name in args.instances)
    evaluator = replace(
        DEFAULT_CONFIG.evaluator,
        battery_constraints_enabled=args.mode == "evrptw",
    )
    operators = replace(
        DEFAULT_CONFIG.operators,
        local_search_probability=args.local_search_probability,
    )
    adaptive = replace(
        DEFAULT_CONFIG.adaptive_weights,
        enabled=not args.disable_adaptive,
    )
    simulated_annealing = replace(
        DEFAULT_CONFIG.simulated_annealing,
        enabled=not args.disable_sa,
    )
    experiment = replace(
        DEFAULT_CONFIG.experiment,
        instance_names=instance_names,
        seeds=tuple(args.seeds),
        iterations=args.iterations,
        time_limit_s=None if args.time_limit == 0 else args.time_limit,
        output_dir=args.output_dir.resolve(),
    )
    return Week6Config(
        evaluator=evaluator,
        operators=operators,
        adaptive_weights=adaptive,
        simulated_annealing=simulated_annealing,
        experiment=experiment,
    )


def result_row(
    method: str,
    instance_name: str,
    seed: int,
    result: ALNSResult,
) -> dict[str, object]:
    evaluation = result.best_evaluation
    return {
        "method": method,
        "instance": instance_name,
        "seed": seed,
        "feasible": evaluation.feasible,
        "vehicle_count": evaluation.vehicle_count,
        "total_distance": round(evaluation.total_distance, 6),
        "runtime_s": round(result.runtime_s, 6),
        "iterations": result.iterations_completed,
        "best_iteration": result.best_iteration,
        "accepted_moves": result.accepted_moves,
        "improving_moves": result.improving_moves,
        "neutral_moves": result.neutral_moves,
        "accepted_worse_moves": result.accepted_worse_moves,
        "termination_reason": result.termination_reason,
        "time_limit_hit": result.time_limit_hit,
        "missing_customer_count": len(evaluation.missing_customers),
        "duplicate_customer_count": len(evaluation.duplicate_customers),
        "late_customer_count": evaluation.late_customer_count,
        "route_structure_violation": (
            evaluation.route_structure_violation
        ),
        "capacity_violation": round(
            evaluation.capacity_violation,
            6,
        ),
        "time_window_violation": round(
            evaluation.time_window_violation,
            6,
        ),
        "energy_violation": round(evaluation.energy_violation, 6),
        "minimum_battery": round(evaluation.minimum_battery, 6),
        "station_visits": evaluation.station_visits,
        "charging_time": round(evaluation.total_charging_time, 6),
        "waiting_time": round(evaluation.total_waiting_time, 6),
        "destroy_weights": json.dumps(
            result.destroy_weights,
            sort_keys=True,
        ),
        "repair_weights": json.dumps(
            result.repair_weights,
            sort_keys=True,
        ),
        "routes": json.dumps(result.best_solution.routes),
    }


def write_results(
    rows: list[dict[str, object]],
    config: Week6Config,
    mode: str,
) -> tuple[Path, Path]:
    output_dir = config.experiment.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / f"alns_{mode}_summary.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    metadata_path = output_dir / f"alns_{mode}_config.json"
    metadata_path.write_text(
        json.dumps(asdict(config), indent=2, default=str),
        encoding="utf-8",
    )
    return csv_path, metadata_path


def main() -> None:
    args = parse_args()
    config = build_config(args)
    instances = {}

    for instance_name in config.experiment.instance_names:
        path = config.experiment.data_dir / f"{instance_name}.txt"
        instance = load_schneider_instance(path)
        instances[instance_name] = instance
        print(
            f"{instance.name}: {len(instance.customer_ids)} customers, "
            f"{len(instance.station_ids)} stations, "
            f"Q={instance.battery_capacity}, C={instance.vehicle_capacity}"
        )

    if args.check_config:
        print(json.dumps(asdict(config), indent=2, default=str))
        return

    method = (
        "ALNS_EVRPTW_FULL_RECHARGE"
        if args.mode == "evrptw"
        else "ALNS_VRPTW"
    )
    rows: list[dict[str, object]] = []
    for instance_name, instance in instances.items():
        for seed in config.experiment.seeds:
            print(f"Running {method}: {instance_name}, seed={seed}")
            result = solve(instance, config, seed)
            row = result_row(method, instance_name, seed, result)
            rows.append(row)
            print(
                "  "
                f"feasible={row['feasible']} "
                f"vehicles={row['vehicle_count']} "
                f"distance={row['total_distance']} "
                f"runtime={row['runtime_s']}s"
            )

    csv_path, metadata_path = write_results(
        rows,
        config,
        args.mode,
    )
    print(f"Saved summary: {csv_path}")
    print(f"Saved config:  {metadata_path}")


if __name__ == "__main__":
    main()
