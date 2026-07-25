"""
EVRPTWEnv — Electric Vehicle Routing Problem with Time Windows Environment
Replicates Lin, Ghaddar & Nathwani (2021), IEEE TITS, arXiv:2010.02068

Node ordering in state tensors:
  idx 0              → depot
  idx 1..n_customer  → customers
  idx n_customer+1.. → charging stations

State keys (TensorDict):
  locs          [B, N, 2]    normalised coordinates
  demand        [B, N]       customer demand (0 for depot/station)
  time_windows  [B, N, 2]    [earliest, latest] service start
  service_time  [B, N]       service duration
  node_type     [B, N]       0=depot, 1=customer, 2=station
  current_node  [B]          current vehicle position index
  battery       [B]          remaining battery  (0..battery_capacity)
  current_time  [B]          elapsed time  (normalised)
  used_capacity [B]          current vehicle load
  visited       [B, 1, N]    bool, True = customer already served
  action_mask   [B, N]       bool, True = node is AVAILABLE (RL4CO convention)
  i             [B]          step counter

Battery design (Lin et al.):
  battery_capacity  default 3.0  (> √2 so any node is reachable from any position)
  energy_rate       1.0 per unit distance
  charge_rate       (battery_capacity - b) * g_norm  where g_norm = 0.2
                    → full recharge from 0 takes 0.2*battery_capacity time units
"""

import torch
from tensordict.tensordict import TensorDict
from rl4co.envs.common.base import RL4COEnvBase
from rl4co.utils.pylogger import get_pylogger

# torchrl spec compatibility shim (API changed in torchrl ≥ 0.3.0)
try:
    from torchrl.data import (
        BoundedTensorSpec, CompositeSpec,
        UnboundedContinuousTensorSpec, UnboundedDiscreteTensorSpec,
    )
except ImportError:
    try:
        from torchrl.data import (
            Bounded as BoundedTensorSpec, Composite as CompositeSpec,
            Unbounded as UnboundedContinuousTensorSpec,
            UnboundedDiscrete as UnboundedDiscreteTensorSpec,
        )
    except ImportError:
        class _Stub:
            def __init__(self, *a, **kw): pass
        BoundedTensorSpec = UnboundedContinuousTensorSpec = \
            UnboundedDiscreteTensorSpec = CompositeSpec = _Stub

from labs.week6.src.data.generator import EVRPTWGenerator

log = get_pylogger(__name__)

DEPOT    = 0
CUSTOMER = 1
STATION  = 2


class EVRPTWEnv(RL4COEnvBase):
    """EVRP-TW environment compatible with RL4CO's AttentionModel."""

    name = "evrptw"

    def __init__(
        self,
        n_customer: int = 20,
        n_station:  int = 5,
        battery_capacity: float = 3.0,  # > √2 ensures full grid coverage
        charge_g: float = 0.2,          # time per unit of energy recharged
        generator_params: dict = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.n_customer       = n_customer
        self.n_station        = n_station
        self.n_nodes          = 1 + n_customer + n_station
        self.battery_capacity = battery_capacity
        self.charge_g         = charge_g   # charge_time = (B_cap - b) * g

        gen_params = generator_params or {}
        gen_params.setdefault("n_customer", n_customer)
        gen_params.setdefault("n_station",  n_station)
        self.generator = EVRPTWGenerator(**gen_params)

        self._make_spec(None)

    # ─── Spec ────────────────────────────────────────────────────────────────

    def _make_spec(self, td_params):
        N  = self.n_nodes
        BC = self.battery_capacity
        try:
            self.observation_spec = CompositeSpec(
                locs          = BoundedTensorSpec(low=0., high=1., shape=(N, 2)),
                demand        = BoundedTensorSpec(low=0., high=1., shape=(N,)),
                time_windows  = BoundedTensorSpec(low=0., high=1., shape=(N, 2)),
                service_time  = BoundedTensorSpec(low=0., high=1., shape=(N,)),
                node_type     = UnboundedDiscreteTensorSpec(shape=(N,), dtype=torch.long),
                current_node  = UnboundedDiscreteTensorSpec(shape=(), dtype=torch.long),
                battery       = BoundedTensorSpec(low=0., high=BC, shape=()),
                current_time  = BoundedTensorSpec(low=0., high=10., shape=()),
                used_capacity = BoundedTensorSpec(low=0., high=1., shape=()),
                visited       = UnboundedDiscreteTensorSpec(shape=(1, N), dtype=torch.bool),
                action_mask   = UnboundedDiscreteTensorSpec(shape=(N,), dtype=torch.bool),
                i             = UnboundedDiscreteTensorSpec(shape=(), dtype=torch.long),
                shape=(),
            )
            self.action_spec = BoundedTensorSpec(
                low=0, high=N - 1, shape=(), dtype=torch.long
            )
            self.reward_spec = UnboundedContinuousTensorSpec(shape=())
            self.done_spec   = UnboundedDiscreteTensorSpec(shape=(), dtype=torch.bool)
        except Exception:
            pass  # specs are advisory; skip if API incompatible

    # ─── Utilities ───────────────────────────────────────────────────────────

    @staticmethod
    def _to_int(batch_size, td=None):
        """Robustly extract scalar batch size."""
        if isinstance(batch_size, (list, tuple)) and len(batch_size) > 0:
            return int(batch_size[0])
        if hasattr(batch_size, "__len__") and len(batch_size) > 0:
            return int(batch_size[0])
        if isinstance(batch_size, int):
            return batch_size
        if td is not None:
            return td["locs"].shape[0]
        raise ValueError(f"Cannot determine batch size from {batch_size!r}")

    # ─── Reset ───────────────────────────────────────────────────────────────

    def _reset(self, td: TensorDict = None, batch_size=None) -> TensorDict:
        if batch_size is None:
            batch_size = self.batch_size if td is None else td.batch_size

        if td is None or td.is_empty():
            td = self.generator(batch_size=batch_size)

        B      = self._to_int(batch_size, td)
        N      = self.n_nodes
        device = td["locs"].device   # match CPU / MPS / CUDA

        td_reset = TensorDict(
            {
                "locs":          td["locs"],
                "demand":        td["demand"],
                "time_windows":  td["time_windows"],
                "service_time":  td["service_time"],
                "node_type":     td["node_type"],
                # ── dynamic state ──────────────────────────────────────────
                "current_node":  torch.zeros(B, dtype=torch.long, device=device),
                "battery":       torch.full((B,), self.battery_capacity, device=device),
                "current_time":  torch.zeros(B, device=device),
                "used_capacity": torch.zeros(B, device=device),
                "visited":       torch.zeros(B, 1, N, dtype=torch.bool, device=device),
                "i":             torch.zeros(B, dtype=torch.long, device=device),
            },
            batch_size=[B],
        )
        # RL4CO decoder reads action_mask — True = AVAILABLE
        td_reset.set("action_mask", ~self._infeasible(td_reset))
        return td_reset

    # ─── Step ────────────────────────────────────────────────────────────────

    def _step(self, td: TensorDict) -> TensorDict:
        action        = td["action"].reshape(-1)          # [B]
        B             = action.shape[0]
        locs          = td["locs"]                        # [B, N, 2]
        node_type     = td["node_type"]                   # [B, N]
        battery       = td["battery"].clone()             # [B]
        current_time  = td["current_time"].clone()        # [B]
        used_capacity = td["used_capacity"].clone()       # [B]
        visited       = td["visited"].clone()             # [B, 1, N]
        service_time  = td["service_time"]                # [B, N]
        demand        = td["demand"]                      # [B, N]
        time_windows  = td["time_windows"]                # [B, N, 2]
        current_node  = td["current_node"]                # [B]
        device        = locs.device

        # ── 1. Travel ─────────────────────────────────────────────────────
        curr_locs = locs.gather(1, current_node.view(B, 1, 1).expand(B, 1, 2)).squeeze(1)
        next_locs = locs.gather(1, action.view(B, 1, 1).expand(B, 1, 2)).squeeze(1)
        dist = torch.norm(next_locs - curr_locs, dim=-1)   # [B]

        battery      = (battery - dist).clamp(min=0.)
        current_time = current_time + dist

        # ── 2. Wait if arriving before TW opens ───────────────────────────
        tw_e = time_windows.gather(
            1, action.view(B, 1, 1).expand(B, 1, 2)
        ).squeeze(1)[:, 0]                                # [B]  tw_early
        current_time = torch.max(current_time, tw_e)

        # ── 3. Node-type updates ──────────────────────────────────────────
        action_type = node_type.gather(1, action.unsqueeze(1)).squeeze(1)  # [B]
        is_station  = (action_type == STATION)
        is_customer = (action_type == CUSTOMER)
        is_depot    = (action_type == DEPOT)

        # Charging station → full recharge, charging takes (B_cap - b) * g
        charge_time = (self.battery_capacity - battery) * self.charge_g
        current_time = current_time + charge_time * is_station.float()
        battery = torch.where(
            is_station,
            torch.full_like(battery, self.battery_capacity),
            battery,
        )

        # Depot → recharge battery (new vehicle departs with full battery).
        # Lin et al. is a multi-route problem: depot return = end of one route,
        # next vehicle starts fresh. Capacity reset handled below.
        battery = torch.where(
            is_depot,
            torch.full_like(battery, self.battery_capacity),
            battery,
        )

        # Customer → add service time, update load
        svc = service_time.gather(1, action.unsqueeze(1)).squeeze(1)   # [B]
        current_time  = current_time + svc * is_customer.float()
        dem = demand.gather(1, action.unsqueeze(1)).squeeze(1)          # [B]
        used_capacity = used_capacity + dem * is_customer.float()

        # Depot → start new vehicle route:
        #   reset load, reset time to 0 (each vehicle departs at t=0,
        #   consistent with Lin et al. multi-vehicle EVRP-TW formulation)
        used_capacity = torch.where(
            is_depot, torch.zeros_like(used_capacity), used_capacity
        )
        current_time = torch.where(
            is_depot, torch.zeros_like(current_time), current_time
        )

        # ── 4. Mark visited ───────────────────────────────────────────────
        action_onehot = torch.zeros(B, 1, self.n_nodes, device=device)
        action_onehot.scatter_(2, action.view(B, 1, 1), 1.)
        cust_flag = is_customer.view(B, 1, 1).expand_as(action_onehot)
        visited = visited | (cust_flag & action_onehot.bool())

        # ── 5. Done ───────────────────────────────────────────────────────
        all_visited = visited.squeeze(1)[:, 1:1 + self.n_customer].all(dim=-1)
        done = all_visited & is_depot

        # ── 6. Build next state ───────────────────────────────────────────
        next_td = td.clone()
        next_td.update({
            "current_node":  action,
            "battery":       battery,
            "current_time":  current_time,
            "used_capacity": used_capacity,
            "visited":       visited,
            "i":             td["i"] + 1,
            "reward":        torch.zeros(B, device=device),
            "done":          done,
        })
        next_td.set("action_mask", ~self._infeasible(next_td))
        return next_td

    # ─── Reward ──────────────────────────────────────────────────────────────

    def _get_reward(self, td: TensorDict, actions: torch.Tensor) -> torch.Tensor:
        """Reward = negative total tour distance.  actions: [B, T]"""
        locs   = td["locs"]
        B, T   = actions.shape
        device = locs.device
        depot  = torch.zeros(B, 1, dtype=torch.long, device=device)
        seq    = torch.cat([depot, actions], dim=1)          # [B, T+1]
        pts    = locs.gather(1, seq.unsqueeze(-1).expand(B, T + 1, 2))
        dists  = torch.norm(pts[:, 1:] - pts[:, :-1], dim=-1)
        return -dists.sum(dim=-1)

    # ─── Feasibility check (RL4CO hook) ──────────────────────────────────────

    def check_solution_validity(self, td: TensorDict, actions: torch.Tensor):
        """Skip hard validity check during training — reward already penalises distance."""
        pass

    # ─── Infeasibility mask ───────────────────────────────────────────────────

    def _infeasible(self, td: TensorDict) -> torch.Tensor:
        """
        Returns [B, N] bool where True = node is INFEASIBLE to visit.

        Rules:
          Battery: battery_after_travel(j) < dist(j, nearest_charger)
          TW:      arrival(j) > tw_late(j)       [customers only]
          Cap:     used_cap + demand(j) > 1.0    [customers only]
          Visited: already served                 [customers only]
          Depot:   always accessible (override at end)
          Terminal: all customers done → force return to depot
        """
        B             = td.batch_size[0]
        N             = self.n_nodes
        locs          = td["locs"]
        battery       = td["battery"]
        current_time  = td["current_time"]
        current_node  = td["current_node"]
        visited       = td["visited"].squeeze(1)        # [B, N]
        time_windows  = td["time_windows"]
        node_type     = td["node_type"]
        used_capacity = td["used_capacity"]
        demand        = td["demand"]
        device        = locs.device

        # Distance: current → each node
        curr_locs  = locs.gather(1, current_node.view(B, 1, 1).expand(B, 1, 2)).squeeze(1)
        dist_to_all = torch.norm(locs - curr_locs.unsqueeze(1), dim=-1)   # [B, N]

        # ── Battery ───────────────────────────────────────────────────────
        is_charger = (node_type == DEPOT) | (node_type == STATION)        # [B, N]
        pairwise   = torch.norm(locs.unsqueeze(2) - locs.unsqueeze(1), dim=-1)  # [B, N, N]
        big        = torch.full_like(pairwise, 1e6)
        charger_expand = is_charger.unsqueeze(1).expand(B, N, N)
        min_to_charger = torch.where(charger_expand, pairwise, big).min(dim=-1).values  # [B, N]

        bat_after    = battery.unsqueeze(1) - dist_to_all   # [B, N]
        battery_mask = bat_after < min_to_charger

        # ── Time window (customers only) ──────────────────────────────────
        arrival  = current_time.unsqueeze(1) + dist_to_all  # [B, N]
        tw_late  = time_windows[:, :, 1]
        tw_mask  = (arrival > tw_late) & (node_type == CUSTOMER)

        # ── Capacity (customers only) ─────────────────────────────────────
        cap_mask = ((used_capacity.unsqueeze(1) + demand) > 1.0) & (node_type == CUSTOMER)

        # ── Already visited ───────────────────────────────────────────────
        vis_mask = visited & (node_type == CUSTOMER)

        # ── Combine ───────────────────────────────────────────────────────
        mask = battery_mask | tw_mask | cap_mask | vis_mask   # True = infeasible

        # Depot is always accessible
        mask[:, 0] = False

        # If all customers done → force depot return
        all_done = visited[:, 1:1 + self.n_customer].all(dim=-1)   # [B]
        force    = all_done.unsqueeze(1).expand(B, N)
        depot_only = torch.ones(B, N, dtype=torch.bool, device=device)
        depot_only[:, 0] = False
        mask = torch.where(force, depot_only, mask)

        return mask   # True = infeasible

    # ─── Public mask alias (smoke_test / eval compat) ────────────────────────

    def get_action_mask(self, td: TensorDict) -> torch.Tensor:
        """True = CANNOT visit (infeasible).  Used in smoke_test and eval scripts."""
        return self._infeasible(td)

    # ─── Observation ─────────────────────────────────────────────────────────

    def _get_obs(self, td: TensorDict) -> TensorDict:
        return td

    # ─── Render ──────────────────────────────────────────────────────────────

    def render(self, td: TensorDict, actions=None, ax=None):
        import matplotlib.pyplot as plt
        if ax is None:
            _, ax = plt.subplots(figsize=(6, 6))
        locs      = td["locs"][0].cpu().numpy()
        node_type = td["node_type"][0].cpu().numpy()
        styles = {DEPOT: ("black","s",80,"Depot"),
                  CUSTOMER: ("steelblue","o",30,"Customer"),
                  STATION: ("green","^",40,"Station")}
        for nt, (c, m, s, lbl) in styles.items():
            idx = node_type == nt
            ax.scatter(locs[idx,0], locs[idx,1], c=c, marker=m, s=s, label=lbl, zorder=3)
        if actions is not None:
            tour = [0] + actions[0].cpu().tolist() + [0]
            ax.plot([locs[i,0] for i in tour], [locs[i,1] for i in tour],
                    "gray", lw=0.8, zorder=2)
        ax.legend(fontsize=8)
        ax.set_title("EVRP-TW Instance")
        return ax
