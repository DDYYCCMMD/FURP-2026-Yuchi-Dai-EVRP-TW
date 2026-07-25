"""Week 6 step 1: Schneider parameters must remain in raw units."""

from labs.week6.src.alns.config import PROJECT_ROOT
from labs.week6.src.alns.instance_loader import load_schneider_instance


def test_load_small_schneider_instance() -> None:
    path = PROJECT_ROOT / "data" / "schneider_instances" / "c101C5.txt"
    instance = load_schneider_instance(path)

    assert instance.depot_id == "D0"
    assert len(instance.customer_ids) == 5
    assert len(instance.station_ids) >= 1
    assert instance.battery_capacity == 77.75
    assert instance.vehicle_capacity == 200.0
    assert instance.energy_rate == 1.0
    assert instance.vehicle_speed == 1.0
