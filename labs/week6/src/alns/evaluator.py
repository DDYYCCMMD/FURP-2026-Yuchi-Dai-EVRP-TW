"""Unified Week 6 capacity, time-window, and battery evaluator.

Implementation step 2
---------------------
For every route, propagate state in this exact order:
1. travel and consume energy;
2. record negative-battery violation before any clamp/recharge;
3. compute arrival, waiting, and service start;
4. check the node time window;
5. update demand/service or perform a full recharge;
6. aggregate customer coverage and route-level metrics.

All construction, repair, and local-search operators must call this module
instead of duplicating feasibility logic.
"""

from __future__ import annotations

from collections import Counter

from .config import EvaluatorConfig
from .models import (
    EVRPTWInstance,
    Evaluation,
    NodeType,
    RouteEvaluation,
    Solution,
)


def evaluate_route(
    instance: EVRPTWInstance,
    route: list[str],
    config: EvaluatorConfig,
) -> RouteEvaluation:
    """Propagate time, load, and battery along one route.

    Battery is never clamped before recording a violation. At a station the
    route is still marked energy-infeasible when arrival battery is negative,
    but state propagation continues after a full recharge so later violations
    remain observable.
    """

    tolerance = config.feasibility_tolerance
    depot_id = instance.depot_id
    structure_violation = (
        len(route) < 2
        or route[0] != depot_id
        or route[-1] != depot_id
        or any(node_id not in instance.nodes for node_id in route)
        or any(node_id == depot_id for node_id in route[1:-1])
    )
    if structure_violation:
        return RouteEvaluation(
            minimum_battery=instance.battery_capacity,
            route_structure_violation=True,
            feasible=False,
        )

    current_time = max(0.0, instance.nodes[depot_id].ready_time)
    load = 0.0
    battery = instance.battery_capacity
    minimum_battery = battery
    total_distance = 0.0
    total_travel_time = 0.0
    total_waiting_time = 0.0
    total_charging_time = 0.0
    capacity_violation = 0.0
    time_window_violation = 0.0
    energy_violation = 0.0
    late_customer_count = 0
    station_visits = 0
    first_energy_failure_index: int | None = None

    for target_index in range(1, len(route)):
        source_id = route[target_index - 1]
        target_id = route[target_index]
        target = instance.nodes[target_id]

        distance = instance.distance(source_id, target_id)
        travel_time = distance / instance.vehicle_speed
        energy_used = distance * instance.energy_rate

        total_distance += distance
        total_travel_time += travel_time
        current_time += travel_time
        battery -= energy_used
        minimum_battery = min(minimum_battery, battery)

        if battery < -tolerance:
            energy_violation += -battery
            if first_energy_failure_index is None:
                first_energy_failure_index = target_index

        service_start = max(current_time, target.ready_time)
        total_waiting_time += max(0.0, target.ready_time - current_time)
        lateness = max(0.0, service_start - target.due_time)
        time_window_violation += lateness
        if lateness > tolerance and target.node_type is NodeType.CUSTOMER:
            late_customer_count += 1

        current_time = service_start
        if target.node_type is NodeType.CUSTOMER:
            load += target.demand
            capacity_violation = max(
                capacity_violation,
                load - instance.vehicle_capacity,
            )
            current_time += target.service_time
        elif target.node_type is NodeType.STATION:
            station_visits += 1
            charge_amount = max(0.0, instance.battery_capacity - battery)
            charging_time = instance.inverse_refuel_rate * charge_amount
            total_charging_time += charging_time
            current_time += charging_time
            battery = instance.battery_capacity

    energy_is_feasible = (
        not config.battery_constraints_enabled
        or energy_violation <= tolerance
    )
    feasible = (
        not structure_violation
        and capacity_violation <= tolerance
        and time_window_violation <= tolerance
        and energy_is_feasible
    )
    return RouteEvaluation(
        total_distance=total_distance,
        total_travel_time=total_travel_time,
        total_waiting_time=total_waiting_time,
        total_charging_time=total_charging_time,
        station_visits=station_visits,
        capacity_violation=max(0.0, capacity_violation),
        time_window_violation=time_window_violation,
        energy_violation=energy_violation,
        late_customer_count=late_customer_count,
        minimum_battery=minimum_battery,
        first_energy_failure_index=first_energy_failure_index,
        route_structure_violation=structure_violation,
        feasible=feasible,
    )


def evaluate_solution(
    instance: EVRPTWInstance,
    solution: Solution,
    config: EvaluatorConfig,
) -> Evaluation:
    """Evaluate all routes and enforce exactly-once customer coverage."""

    route_metrics = [
        evaluate_route(instance, route, config) for route in solution.routes
    ]
    served = Counter(
        node_id
        for route in solution.routes
        for node_id in route
        if node_id in instance.nodes
        and instance.nodes[node_id].node_type is NodeType.CUSTOMER
    )
    expected = set(instance.customer_ids)
    missing_customers = tuple(sorted(expected - served.keys()))
    duplicate_customers = tuple(
        sorted(node_id for node_id, count in served.items() if count > 1)
    )
    active_routes = sum(
        any(
            node_id in instance.nodes
            and instance.nodes[node_id].node_type is NodeType.CUSTOMER
            for node_id in route
        )
        for route in solution.routes
    )
    tolerance = config.feasibility_tolerance
    capacity_violation = sum(
        metric.capacity_violation for metric in route_metrics
    )
    time_window_violation = sum(
        metric.time_window_violation for metric in route_metrics
    )
    energy_violation = sum(
        metric.energy_violation for metric in route_metrics
    )
    route_structure_violation = any(
        metric.route_structure_violation for metric in route_metrics
    )
    energy_is_feasible = (
        not config.battery_constraints_enabled
        or energy_violation <= tolerance
    )
    feasible = (
        not missing_customers
        and not duplicate_customers
        and not route_structure_violation
        and capacity_violation <= tolerance
        and time_window_violation <= tolerance
        and energy_is_feasible
    )

    return Evaluation(
        total_distance=sum(metric.total_distance for metric in route_metrics),
        total_travel_time=sum(
            metric.total_travel_time for metric in route_metrics
        ),
        total_waiting_time=sum(
            metric.total_waiting_time for metric in route_metrics
        ),
        total_charging_time=sum(
            metric.total_charging_time for metric in route_metrics
        ),
        vehicle_count=active_routes,
        station_visits=sum(metric.station_visits for metric in route_metrics),
        capacity_violation=capacity_violation,
        time_window_violation=time_window_violation,
        energy_violation=energy_violation,
        late_customer_count=sum(
            metric.late_customer_count for metric in route_metrics
        ),
        minimum_battery=min(
            (metric.minimum_battery for metric in route_metrics),
            default=instance.battery_capacity,
        ),
        missing_customers=missing_customers,
        duplicate_customers=duplicate_customers,
        route_structure_violation=route_structure_violation,
        feasible=feasible,
    )
