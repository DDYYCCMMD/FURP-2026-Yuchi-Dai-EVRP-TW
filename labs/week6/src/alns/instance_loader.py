"""Raw-unit Schneider benchmark loader for ``labs/week6``.

This is separate from ``src/data/schneider_loader.py`` because the RL loader
normalises tensors. The ALNS evaluator needs coordinates, time, energy, and
charging parameters in mutually consistent original units.
"""

from __future__ import annotations

import re
from pathlib import Path

from .models import EVRPTWInstance, Node, NodeType


_PARAMETER_PATTERN = re.compile(
    r"^([QCrgv])\s+.+?/([0-9.eE+-]+)/"
)


def load_schneider_instance(path: str | Path) -> EVRPTWInstance:
    """Parse one Schneider ``.txt`` file without normalisation.

    Step 1: parse depot, stations, and customers.
    Step 2: parse Q/C/r/g/v from the footer.
    Step 3: validate the minimum data needed by the evaluator.
    """

    path = Path(path)
    nodes: dict[str, Node] = {}
    parameters: dict[str, float] = {}

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue

        parameter_match = _PARAMETER_PATTERN.match(line)
        if parameter_match:
            parameters[parameter_match.group(1)] = float(
                parameter_match.group(2)
            )
            continue

        fields = line.split()
        if len(fields) < 8 or fields[1].lower() not in {"d", "f", "c"}:
            continue

        node_id = fields[0]
        if node_id in nodes:
            raise ValueError(f"duplicate node id {node_id!r} in {path}")

        nodes[node_id] = Node(
            node_id=node_id,
            node_type=NodeType(fields[1].lower()),
            x=float(fields[2]),
            y=float(fields[3]),
            demand=float(fields[4]),
            ready_time=float(fields[5]),
            due_time=float(fields[6]),
            service_time=float(fields[7]),
        )

    missing_parameters = {"Q", "C", "r", "g", "v"} - parameters.keys()
    if missing_parameters:
        raise ValueError(
            f"{path} is missing parameters: {sorted(missing_parameters)}"
        )
    if not nodes:
        raise ValueError(f"no nodes found in {path}")

    instance = EVRPTWInstance(
        name=path.stem,
        nodes=nodes,
        battery_capacity=parameters["Q"],
        vehicle_capacity=parameters["C"],
        energy_rate=parameters["r"],
        inverse_refuel_rate=parameters["g"],
        vehicle_speed=parameters["v"],
    )
    _ = instance.depot_id  # Trigger the exactly-one-depot validation.
    return instance
