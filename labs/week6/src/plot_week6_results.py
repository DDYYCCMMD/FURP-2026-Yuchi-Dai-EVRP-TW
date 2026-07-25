#!/usr/bin/env python3
"""Generate the Week 6 ALNS-EVRPTW report figures.

The script reads only the fixed-iteration formal CSV files:

- ``results/week6/main_fixed1000``;
- ``results/week6/ablation_no_adaptive``;
- ``results/week6/ablation_no_sa``;
- ``results/week6/ablation_no_local_search``.

It deliberately excludes the old time-capped pilot and smoke outputs.
"""

from __future__ import annotations

import csv
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean


PROJECT_ROOT = Path(__file__).resolve().parents[3]
os.environ.setdefault(
    "MPLCONFIGDIR",
    str(PROJECT_ROOT / "results" / "mplconfig"),
)

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402


RESULT_ROOT = PROJECT_ROOT / "results" / "week6"
FIGURE_DIR = PROJECT_ROOT / "docs" / "figures" / "week06"
TOLERANCE = 1e-6

SOURCE_FILES = {
    "vrptw": (
        RESULT_ROOT
        / "main_fixed1000"
        / "alns_vrptw_summary.csv"
    ),
    "full": (
        RESULT_ROOT
        / "main_fixed1000"
        / "alns_evrptw_summary.csv"
    ),
    "no_adaptive": (
        RESULT_ROOT
        / "ablation_no_adaptive"
        / "alns_evrptw_summary.csv"
    ),
    "no_sa": (
        RESULT_ROOT
        / "ablation_no_sa"
        / "alns_evrptw_summary.csv"
    ),
    "no_local_search": (
        RESULT_ROOT
        / "ablation_no_local_search"
        / "alns_evrptw_summary.csv"
    ),
}

METHOD_LABELS = {
    "vrptw": "ALNS-VRPTW",
    "full": "Full ALNS-EVRPTW",
    "no_adaptive": "No adaptive",
    "no_sa": "No SA",
    "no_local_search": "No local search",
}

NAVY = "#1F4E78"
BLUE = "#4C78A8"
TEAL = "#1B998B"
ORANGE = "#F28E2B"
RED = "#D95F5F"
GRAY = "#A7A9AC"
LIGHT_BLUE = "#DCE6F1"
LIGHT_TEAL = "#DDF2EE"
LIGHT_ORANGE = "#FCE8D2"
DARK = "#263238"


def configure_style() -> None:
    """Use one restrained report style across every figure."""

    plt.rcParams.update(
        {
            "figure.dpi": 130,
            "savefig.dpi": 240,
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "axes.titleweight": "bold",
            "axes.edgecolor": "#9AA0A6",
            "axes.linewidth": 0.8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "legend.frameon": False,
            "grid.color": "#D9DEE3",
            "grid.alpha": 0.65,
            "grid.linewidth": 0.7,
            "text.color": DARK,
            "axes.labelcolor": DARK,
            "xtick.color": DARK,
            "ytick.color": DARK,
        }
    )


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_all() -> dict[str, list[dict[str, str]]]:
    rows = {
        method: load_rows(path)
        for method, path in SOURCE_FILES.items()
    }
    for method, method_rows in rows.items():
        if len(method_rows) != 54:
            raise ValueError(
                f"{method} must contain 54 formal rows, "
                f"found {len(method_rows)}"
            )
    return rows


def row_key(row: dict[str, str]) -> tuple[str, int]:
    return row["instance"], int(row["seed"])


def objective(row: dict[str, str]) -> tuple[int, float]:
    return int(row["vehicle_count"]), float(row["total_distance"])


def compare_objective(
    left: dict[str, str],
    right: dict[str, str],
) -> int:
    """Return -1 if left is better, 0 if tied, and 1 if worse."""

    left_vehicle, left_distance = objective(left)
    right_vehicle, right_distance = objective(right)
    if left_vehicle != right_vehicle:
        return -1 if left_vehicle < right_vehicle else 1
    delta = left_distance - right_distance
    if abs(delta) <= TOLERANCE:
        return 0
    return -1 if delta < 0 else 1


def customer_count(instance: str) -> int:
    match = re.search(r"C(\d+)$", instance)
    if match is None:
        raise ValueError(f"cannot parse customer count from {instance}")
    return int(match.group(1))


def instance_family(instance: str) -> str:
    if instance.startswith("rc"):
        return "RC"
    if instance.startswith("r"):
        return "R"
    return "C"


def save_figure(fig: plt.Figure, filename: str) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        FIGURE_DIR / filename,
        bbox_inches="tight",
        facecolor="white",
    )
    plt.close(fig)


def add_box(
    ax: plt.Axes,
    center: tuple[float, float],
    width: float,
    height: float,
    text: str,
    *,
    fill: str,
    edge: str = NAVY,
    text_color: str = DARK,
    fontsize: float = 10,
) -> FancyBboxPatch:
    """Add a rounded labeled process box in axes coordinates."""

    x = center[0] - width / 2
    y = center[1] - height / 2
    box = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.015,rounding_size=0.02",
        transform=ax.transAxes,
        facecolor=fill,
        edgecolor=edge,
        linewidth=1.4,
    )
    ax.add_patch(box)
    ax.text(
        center[0],
        center[1],
        text,
        transform=ax.transAxes,
        ha="center",
        va="center",
        color=text_color,
        fontsize=fontsize,
        weight="bold",
    )
    return box


def add_arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    connectionstyle: str = "arc3",
    color: str = NAVY,
    width: float = 1.5,
) -> None:
    arrow = FancyArrowPatch(
        start,
        end,
        transform=ax.transAxes,
        arrowstyle="-|>",
        mutation_scale=13,
        linewidth=width,
        color=color,
        connectionstyle=connectionstyle,
    )
    ax.add_patch(arrow)


def plot_method_evolution() -> None:
    fig, ax = plt.subplots(figsize=(12.0, 3.2))
    ax.set_axis_off()
    stages = [
        ("Penalty-based\nGA-VRPTW", LIGHT_ORANGE),
        ("Unified hard-\nconstraint evaluator", LIGHT_BLUE),
        ("Route-based\nALNS-VRPTW", LIGHT_BLUE),
        ("Full-recharge\nALNS-EVRPTW", LIGHT_TEAL),
        ("Future: partial\ncharging", "#ECE8F6"),
    ]
    xs = np.linspace(0.10, 0.90, len(stages))
    for index, ((label, fill), x_position) in enumerate(zip(stages, xs)):
        add_box(
            ax,
            (float(x_position), 0.55),
            0.16,
            0.30,
            label,
            fill=fill,
        )
        if index < len(stages) - 1:
            add_arrow(
                ax,
                (float(x_position + 0.085), 0.55),
                (float(xs[index + 1] - 0.085), 0.55),
            )
    ax.text(
        0.5,
        0.92,
        "Method evolution from a penalty baseline to strict EVRPTW search",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=14,
        weight="bold",
        color=NAVY,
    )
    ax.text(
        0.5,
        0.12,
        "Week 6 scope",
        transform=ax.transAxes,
        ha="center",
        color=TEAL,
        weight="bold",
    )
    ax.annotate(
        "",
        xy=(0.80, 0.20),
        xytext=(0.20, 0.20),
        xycoords="axes fraction",
        arrowprops={
            "arrowstyle": "|-|",
            "color": TEAL,
            "linewidth": 2,
        },
    )
    save_figure(fig, "fig01_method_evolution.png")


def plot_evaluator_flow() -> None:
    fig, ax = plt.subplots(figsize=(8.8, 9.0))
    ax.set_axis_off()
    steps = [
        ("Start from current node state", LIGHT_BLUE),
        ("Travel to next node\nconsume time and energy", LIGHT_BLUE),
        ("Record battery arrival\nbefore recharge", LIGHT_ORANGE),
        ("Compute arrival, waiting,\nand service start", LIGHT_BLUE),
        ("Check capacity and\ntime-window feasibility", LIGHT_ORANGE),
        ("Customer service or\nfull station recharge", LIGHT_TEAL),
        ("Aggregate route and\ncustomer-coverage metrics", LIGHT_TEAL),
    ]
    y_positions = np.linspace(0.86, 0.14, len(steps))
    for index, ((label, fill), y_position) in enumerate(
        zip(steps, y_positions)
    ):
        add_box(
            ax,
            (0.39, float(y_position)),
            0.48,
            0.075,
            label,
            fill=fill,
            fontsize=9.5,
        )
        if index < len(steps) - 1:
            add_arrow(
                ax,
                (0.39, float(y_position - 0.045)),
                (0.39, float(y_positions[index + 1] + 0.045)),
            )

    add_box(
        ax,
        (0.79, 0.52),
        0.30,
        0.47,
        (
            "Evaluator outputs\n\n"
            "capacity_violation\n"
            "time_window_violation\n"
            "energy_violation\n"
            "minimum_battery\n"
            "missing / duplicates\n"
            "route structure\n"
            "strict feasibility"
        ),
        fill="#F4F6F7",
        edge=GRAY,
        fontsize=9,
    )
    add_arrow(
        ax,
        (0.64, 0.20),
        (0.68, 0.36),
        connectionstyle="arc3,rad=-0.2",
        color=GRAY,
    )
    ax.set_title(
        "Unified route evaluator: one state-propagation path for every operator",
        color=NAVY,
        pad=18,
    )
    save_figure(fig, "fig02_evaluator_flow.png")


def plot_alns_pipeline() -> None:
    fig, ax = plt.subplots(figsize=(10.4, 8.5))
    ax.set_axis_off()
    steps = [
        ("Initial feasible solution", (0.50, 0.90), LIGHT_BLUE),
        ("Select destroy and\nrepair operators", (0.50, 0.79), LIGHT_BLUE),
        ("Remove customers", (0.25, 0.66), LIGHT_ORANGE),
        ("Customer insertion", (0.50, 0.66), LIGHT_BLUE),
        ("Charging-station repair", (0.75, 0.66), LIGHT_TEAL),
        ("Relocate + 2-opt", (0.75, 0.50), LIGHT_BLUE),
        ("Unified evaluator", (0.50, 0.43), LIGHT_TEAL),
        ("Feasibility-first SA\naccept / reject", (0.25, 0.50), LIGHT_ORANGE),
        ("Update best solution and\nadaptive weights", (0.50, 0.27), LIGHT_BLUE),
    ]
    for label, center, fill in steps:
        add_box(
            ax,
            center,
            0.22 if center[1] != 0.66 else 0.20,
            0.075,
            label,
            fill=fill,
            fontsize=9,
        )
    arrows = [
        ((0.50, 0.855), (0.50, 0.835)),
        ((0.50, 0.745), (0.29, 0.70)),
        ((0.35, 0.66), (0.39, 0.66)),
        ((0.61, 0.66), (0.64, 0.66)),
        ((0.75, 0.615), (0.75, 0.545)),
        ((0.64, 0.49), (0.60, 0.45)),
        ((0.39, 0.44), (0.35, 0.48)),
        ((0.29, 0.455), (0.43, 0.305)),
    ]
    for start, end in arrows:
        add_arrow(ax, start, end)
    ax.plot(
        [0.61, 0.93, 0.93],
        [0.27, 0.27, 0.79],
        transform=ax.transAxes,
        color=TEAL,
        linewidth=1.8,
    )
    add_arrow(
        ax,
        (0.93, 0.79),
        (0.62, 0.79),
        color=TEAL,
        width=1.8,
    )
    ax.text(
        0.80,
        0.845,
        "repeat until\n1,000 iterations",
        transform=ax.transAxes,
        ha="center",
        va="center",
        color=TEAL,
        weight="bold",
    )
    ax.set_title(
        "Week 6 ALNS-EVRPTW search pipeline",
        color=NAVY,
        pad=18,
    )
    save_figure(fig, "fig03_alns_pipeline.png")


def plot_vehicle_count(rows: dict[str, list[dict[str, str]]]) -> None:
    grouped: dict[tuple[str, str], list[float]] = defaultdict(list)
    for method in ("vrptw", "full"):
        for row in rows[method]:
            grouped[(method, row["instance"])].append(
                float(row["vehicle_count"])
            )
    instances = sorted(
        {row["instance"] for row in rows["full"]},
        key=lambda name: (
            customer_count(name),
            ("C", "R", "RC").index(instance_family(name)),
            name,
        ),
    )
    positions = np.arange(len(instances))
    vr_values = [mean(grouped[("vrptw", name)]) for name in instances]
    ev_values = [mean(grouped[("full", name)]) for name in instances]

    fig, ax = plt.subplots(figsize=(9.0, 8.2))
    for position, vr_value, ev_value in zip(
        positions,
        vr_values,
        ev_values,
    ):
        ax.plot(
            [vr_value, ev_value],
            [position, position],
            color=GRAY,
            linewidth=1.7,
            zorder=1,
        )
    ax.scatter(
        vr_values,
        positions,
        s=55,
        color=BLUE,
        label="ALNS-VRPTW",
        zorder=3,
    )
    ax.scatter(
        ev_values,
        positions,
        s=55,
        color=TEAL,
        label="Full ALNS-EVRPTW",
        zorder=3,
    )
    ax.set_yticks(positions, instances)
    ax.invert_yaxis()
    ax.set_xlabel("Mean vehicle count across seeds")
    ax.set_title(
        "Battery constraints never reduce vehicle count in matched runs"
    )
    ax.grid(axis="x")
    ax.legend(loc="lower right")
    for boundary in (5.5, 11.5):
        ax.axhline(boundary, color="#C6CCD2", linewidth=1.0)
    ax.text(
        1.01,
        0.84,
        "5 customers",
        transform=ax.transAxes,
        rotation=90,
        color=GRAY,
        va="center",
    )
    ax.text(
        1.01,
        0.50,
        "10 customers",
        transform=ax.transAxes,
        rotation=90,
        color=GRAY,
        va="center",
    )
    ax.text(
        1.01,
        0.16,
        "15 customers",
        transform=ax.transAxes,
        rotation=90,
        color=GRAY,
        va="center",
    )
    fig.tight_layout()
    save_figure(fig, "fig04_vehicle_count_vr_vs_ev.png")


def plot_equal_vehicle_distance(
    rows: dict[str, list[dict[str, str]]],
) -> None:
    vr_map = {row_key(row): row for row in rows["vrptw"]}
    ev_map = {row_key(row): row for row in rows["full"]}
    deltas: dict[str, list[float]] = defaultdict(list)
    for key, vr_row in vr_map.items():
        ev_row = ev_map[key]
        if int(vr_row["vehicle_count"]) == int(ev_row["vehicle_count"]):
            deltas[key[0]].append(
                float(ev_row["total_distance"])
                - float(vr_row["total_distance"])
            )
    values = sorted(
        (
            (instance, mean(instance_deltas), len(instance_deltas))
            for instance, instance_deltas in deltas.items()
        ),
        key=lambda item: item[1],
    )
    instances = [item[0] for item in values]
    averages = [item[1] for item in values]
    counts = [item[2] for item in values]
    colors = [BLUE if value < 0 else ORANGE for value in averages]

    fig, ax = plt.subplots(figsize=(8.8, 5.8))
    y_positions = np.arange(len(instances))
    bars = ax.barh(y_positions, averages, color=colors, height=0.66)
    ax.axvline(0, color=DARK, linewidth=1.0)
    ax.set_yticks(y_positions, instances)
    ax.set_xlabel(
        "Mean distance difference, EVRPTW − VRPTW "
        "(equal-vehicle pairs only)"
    )
    ax.set_title(
        "Energy feasibility usually adds distance when vehicle counts match"
    )
    ax.grid(axis="x")
    for bar, value, count in zip(bars, averages, counts):
        if value >= 0:
            ax.text(
                value + 0.7,
                bar.get_y() + bar.get_height() / 2,
                f"{value:+.1f}  (n={count})",
                va="center",
                ha="left",
                fontsize=8.5,
            )
        else:
            ax.text(
                value + 0.7,
                bar.get_y() + bar.get_height() / 2,
                f"{value:+.1f}  (n={count})",
                va="center",
                ha="left",
                color="white",
                fontsize=8.5,
                weight="bold",
            )
    fig.tight_layout()
    save_figure(fig, "fig05_equal_vehicle_distance_delta.png")


def plot_scalability(rows: dict[str, list[dict[str, str]]]) -> None:
    sizes = [5, 10, 15]

    def average_metric(
        method: str,
        size: int,
        metric: str,
    ) -> float:
        return mean(
            float(row[metric])
            for row in rows[method]
            if customer_count(row["instance"]) == size
        )

    vr_runtime = [
        average_metric("vrptw", size, "runtime_s") for size in sizes
    ]
    ev_runtime = [
        average_metric("full", size, "runtime_s") for size in sizes
    ]
    ev_vehicles = [
        average_metric("full", size, "vehicle_count") for size in sizes
    ]
    ev_stations = [
        average_metric("full", size, "station_visits") for size in sizes
    ]

    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.6))
    axes[0].plot(
        sizes,
        vr_runtime,
        marker="o",
        linewidth=2.2,
        color=BLUE,
        label="ALNS-VRPTW",
    )
    axes[0].plot(
        sizes,
        ev_runtime,
        marker="o",
        linewidth=2.2,
        color=TEAL,
        label="Full ALNS-EVRPTW",
    )
    axes[0].set_yscale("log")
    axes[0].set_xticks(sizes)
    axes[0].set_xlabel("Customers")
    axes[0].set_ylabel("Mean runtime (s, log scale)")
    axes[0].set_title("EV runtime grows faster with instance size")
    axes[0].grid(axis="y", which="both")
    axes[0].legend()
    for size, vr_value, ev_value in zip(
        sizes,
        vr_runtime,
        ev_runtime,
    ):
        axes[0].text(
            size,
            ev_value * 1.16,
            f"{ev_value / vr_value:.1f}×",
            ha="center",
            color=TEAL,
            fontsize=9,
            weight="bold",
        )

    positions = np.arange(len(sizes))
    width = 0.34
    axes[1].bar(
        positions - width / 2,
        ev_vehicles,
        width,
        color=BLUE,
        label="Vehicles",
    )
    axes[1].bar(
        positions + width / 2,
        ev_stations,
        width,
        color=ORANGE,
        label="Station visits",
    )
    axes[1].set_xticks(positions, [str(size) for size in sizes])
    axes[1].set_xlabel("Customers")
    axes[1].set_ylabel("Mean count")
    axes[1].set_title("Larger EV instances require more routing resources")
    axes[1].grid(axis="y")
    axes[1].legend()
    fig.tight_layout()
    save_figure(fig, "fig06_scalability_and_charging.png")


def plot_ablation(rows: dict[str, list[dict[str, str]]]) -> None:
    full_map = {row_key(row): row for row in rows["full"]}
    methods = ["no_adaptive", "no_sa", "no_local_search"]
    result_counts = {}
    for method in methods:
        method_map = {row_key(row): row for row in rows[method]}
        counts: Counter[str] = Counter()
        for key, full_row in full_map.items():
            comparison = compare_objective(full_row, method_map[key])
            if comparison < 0:
                counts["Full wins"] += 1
            elif comparison > 0:
                counts["Full losses"] += 1
            else:
                counts["Ties"] += 1
        result_counts[method] = counts

    labels = [METHOD_LABELS[method] for method in methods]
    wins = [result_counts[method]["Full wins"] for method in methods]
    ties = [result_counts[method]["Ties"] for method in methods]
    losses = [
        result_counts[method]["Full losses"] for method in methods
    ]
    positions = np.arange(len(methods))

    fig, ax = plt.subplots(figsize=(9.2, 4.6))
    ax.barh(positions, wins, color=TEAL, label="Full wins")
    ax.barh(
        positions,
        ties,
        left=wins,
        color=GRAY,
        label="Ties",
    )
    ax.barh(
        positions,
        losses,
        left=np.array(wins) + np.array(ties),
        color=RED,
        label="Full losses",
    )
    ax.set_yticks(positions, labels)
    ax.invert_yaxis()
    ax.set_xlim(0, 54)
    ax.set_xlabel("Matched instance-seed runs")
    ax.set_title(
        "Most ablation runs tie; local search has the clearest quality effect"
    )
    ax.grid(axis="x")
    ax.legend(ncol=3, loc="lower center", bbox_to_anchor=(0.5, -0.28))
    for index, (win, tie, loss) in enumerate(zip(wins, ties, losses)):
        if win:
            ax.text(win / 2, index, str(win), ha="center", va="center")
        if tie:
            ax.text(
                win + tie / 2,
                index,
                str(tie),
                ha="center",
                va="center",
            )
        if loss:
            ax.text(
                win + tie + loss / 2,
                index,
                str(loss),
                ha="center",
                va="center",
                color="white",
                weight="bold",
            )
    fig.tight_layout()
    save_figure(fig, "fig07_ablation_win_tie_loss.png")


def plot_search_behaviour(
    rows: dict[str, list[dict[str, str]]],
) -> None:
    methods = [
        "vrptw",
        "full",
        "no_adaptive",
        "no_sa",
        "no_local_search",
    ]
    labels = [METHOD_LABELS[method] for method in methods]
    neutral_rates = [
        mean(
            int(row["neutral_moves"]) / int(row["iterations"])
            for row in rows[method]
        )
        for method in methods
    ]
    improving = [
        mean(int(row["improving_moves"]) for row in rows[method])
        for method in methods
    ]
    accepted_worse = [
        mean(int(row["accepted_worse_moves"]) for row in rows[method])
        for method in methods
    ]

    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.8))
    positions = np.arange(len(methods))
    bars = axes[0].bar(
        positions,
        np.array(neutral_rates) * 100,
        color=[BLUE, TEAL, ORANGE, RED, GRAY],
    )
    axes[0].set_xticks(positions, labels, rotation=24, ha="right")
    axes[0].set_ylim(80, 100)
    axes[0].set_ylabel("Neutral moves (% of iterations)")
    axes[0].set_title("All variants spend most iterations on plateaus")
    axes[0].grid(axis="y")
    for bar, rate in zip(bars, neutral_rates):
        axes[0].text(
            bar.get_x() + bar.get_width() / 2,
            rate * 100 + 0.35,
            f"{rate:.1%}",
            ha="center",
            fontsize=8.5,
        )

    width = 0.35
    axes[1].bar(
        positions - width / 2,
        improving,
        width,
        color=TEAL,
        label="Improving",
    )
    axes[1].bar(
        positions + width / 2,
        accepted_worse,
        width,
        color=ORANGE,
        label="SA-accepted worse",
    )
    axes[1].set_xticks(positions, labels, rotation=24, ha="right")
    axes[1].set_ylabel("Mean moves per 1,000 iterations")
    axes[1].set_title("Useful state changes are rare")
    axes[1].grid(axis="y")
    axes[1].legend()
    fig.tight_layout()
    save_figure(fig, "fig08_search_behaviour.png")


def main() -> None:
    configure_style()
    rows = load_all()
    plot_method_evolution()
    plot_evaluator_flow()
    plot_alns_pipeline()
    plot_vehicle_count(rows)
    plot_equal_vehicle_distance(rows)
    plot_scalability(rows)
    plot_ablation(rows)
    plot_search_behaviour(rows)
    print(f"Generated 8 Week 6 figures in {FIGURE_DIR}")


if __name__ == "__main__":
    main()
