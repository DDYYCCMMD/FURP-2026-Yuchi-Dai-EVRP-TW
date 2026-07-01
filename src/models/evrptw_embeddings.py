"""
Custom node and context embeddings for EVRP-TW, following Lin et al. (2021).

Architecture additions over the standard Attention Model (Kool 2019):
  1. EVRPTWInitEmbedding
       - Three-type node embedding (depot / customer / station)
       - Node features: [x, y, demand, tw_e, tw_l, svc, type_onehot(3)]
       - Separate linear projections per node type → embedding_dim

  2. EVRPTWContextEmbedding
       - Extends the AM context vector with battery level and current time
       - Standard AM context: [h_current, h_depot, remaining_cap]
       - Lin et al. context:  [h_current, h_depot, remaining_cap, battery, time]

Both classes follow the RL4CO nn module convention and can be passed directly
to AttentionModel via the `init_embedding` and `context_embedding` arguments.
"""

import torch
import torch.nn as nn
from tensordict.tensordict import TensorDict

# Node type indices
DEPOT    = 0
CUSTOMER = 1
STATION  = 2


class EVRPTWInitEmbedding(nn.Module):
    """
    Initial (static) node embedding for EVRP-TW.

    Input features per node (9-dimensional):
      x, y, demand, tw_early, tw_late, service_time, [depot, customer, station] one-hot

    Each node type uses a dedicated linear layer, then results are combined.
    This mirrors the three-type encoding in Lin et al.

    Parameters
    ----------
    embedding_dim : int
        Output embedding dimension (paper: 128).
    """

    def __init__(self, embedding_dim: int = 128):
        super().__init__()
        self.embedding_dim = embedding_dim

        # Input: x, y, demand, tw_e, tw_l, svc = 6 continuous features
        input_dim = 6

        self.depot_embed   = nn.Linear(input_dim, embedding_dim)
        self.customer_embed = nn.Linear(input_dim, embedding_dim)
        self.station_embed  = nn.Linear(input_dim, embedding_dim)

    def forward(self, td: TensorDict) -> torch.Tensor:
        """
        Parameters
        ----------
        td : TensorDict with keys locs, demand, time_windows, service_time, node_type

        Returns
        -------
        h : [B, N, embedding_dim]
        """
        locs         = td["locs"]           # [B, N, 2]
        demand       = td["demand"]         # [B, N]
        time_windows = td["time_windows"]   # [B, N, 2]
        service_time = td["service_time"]   # [B, N]
        node_type    = td["node_type"]      # [B, N]  int64

        B, N, _ = locs.shape

        # Concatenate raw features
        features = torch.cat(
            [
                locs,                           # x, y          [B, N, 2]
                demand.unsqueeze(-1),           # demand         [B, N, 1]
                time_windows,                   # tw_e, tw_l     [B, N, 2]
                service_time.unsqueeze(-1),     # svc            [B, N, 1]
            ],
            dim=-1,
        )                                       # [B, N, 6]

        # Apply type-specific linear embedding
        h = torch.zeros(B, N, self.embedding_dim, device=locs.device)

        depot_idx   = (node_type == DEPOT)    # [B, N] bool
        cust_idx    = (node_type == CUSTOMER)
        station_idx = (node_type == STATION)

        if depot_idx.any():
            h[depot_idx]   = self.depot_embed(features[depot_idx])
        if cust_idx.any():
            h[cust_idx]    = self.customer_embed(features[cust_idx])
        if station_idx.any():
            h[station_idx] = self.station_embed(features[station_idx])

        return h    # [B, N, embedding_dim]


class EVRPTWContextEmbedding(nn.Module):
    """
    Dynamic context embedding for the decoder.

    Extends the AM context with battery level and current time (Lin et al. §III-C).

    Standard AM context (Kool 2019):
        c_t = [h̄ (global mean), h_current, remaining_capacity]
              projected to embedding_dim

    Lin et al. context:
        c_t = [h_current, h_depot, remaining_capacity, battery_level, current_time]
              projected to embedding_dim

    Parameters
    ----------
    embedding_dim : int
        Node/context embedding dimension.
    """

    def __init__(self, embedding_dim: int = 128):
        super().__init__()
        self.embedding_dim = embedding_dim

        # Input:
        #   h_current (embedding_dim) +
        #   h_depot   (embedding_dim) +
        #   3 scalars (remaining_cap, battery, time)
        # → embedding_dim
        self.project = nn.Linear(embedding_dim * 2 + 3, embedding_dim)

    def forward(
        self,
        embeddings: torch.Tensor,   # [B, N, embedding_dim]  encoder output
        td: TensorDict,
    ) -> torch.Tensor:
        """
        Returns
        -------
        context : [B, embedding_dim]
        """
        B = embeddings.shape[0]
        dim = self.embedding_dim

        current_node  = td["current_node"]   # [B]
        battery       = td["battery"]         # [B]
        current_time  = td["current_time"]    # [B]
        used_capacity = td["used_capacity"]   # [B]

        # h_current: embedding of the vehicle's current node
        h_current = embeddings.gather(
            1, current_node.view(B, 1, 1).expand(B, 1, dim)
        ).squeeze(1)                          # [B, dim]

        # h_depot: embedding of depot (node 0)
        h_depot = embeddings[:, 0, :]         # [B, dim]

        # Remaining capacity (normalised)
        remaining_cap = (1.0 - used_capacity).unsqueeze(-1)   # [B, 1]

        # Battery level [0, 1] and current time [0, 1]
        bat  = battery.unsqueeze(-1)           # [B, 1]
        time = current_time.unsqueeze(-1)      # [B, 1]

        # Concatenate all context features
        ctx_input = torch.cat(
            [h_current, h_depot, remaining_cap, bat, time],
            dim=-1,
        )                                      # [B, dim*2 + 3]

        context = self.project(ctx_input)      # [B, dim]
        return context
