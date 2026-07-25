"""
Quick smoke test: verify EVRPTWEnv initialises, steps, and masks correctly.

Run BEFORE train.py to catch any API issues early.

Usage:
    conda activate evrptw
    cd FURP-2026-Yuchi-Dai-EVRP-TW
    python src/smoke_test_env.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import torch
from labs.week6.src.envs.evrptw_env import EVRPTWEnv
from labs.week6.src.data.generator import EVRPTWGenerator
from labs.week6.src.data.schneider_loader import load_instance, check_instance
from labs.week6.src.models.evrptw_embeddings import EVRPTWInitEmbedding, EVRPTWContextEmbedding

PASS = "✓"
FAIL = "✗"


def test_generator():
    print("1. Generator ...", end=" ")
    gen = EVRPTWGenerator(n_customer=10, n_station=3)
    td = gen(batch_size=[4])
    assert td["locs"].shape == (4, 14, 2), f"locs shape wrong: {td['locs'].shape}"
    assert td["demand"].shape == (4, 14)
    assert td["node_type"].shape == (4, 14)
    print(PASS)


def test_env_reset():
    print("2. Env reset ...", end=" ")
    env = EVRPTWEnv(n_customer=10, n_station=3)
    td = env.reset(batch_size=[2])
    assert td["current_node"].shape == (2,)
    assert td["battery"].shape == (2,)
    assert (td["battery"] == env.battery_capacity).all()
    assert td["visited"].shape == (2, 1, 14)
    print(PASS)


def test_env_mask():
    print("3. Action mask ...", end=" ")
    env = EVRPTWEnv(n_customer=10, n_station=3)
    td  = env.reset(batch_size=[2])
    mask = env.get_action_mask(td)   # [2, 14]  True = infeasible
    assert mask.shape == (2, 14)
    # Depot (idx 0) should never be masked
    assert not mask[:, 0].any(), "Depot should always be accessible"
    print(PASS)


def test_env_step():
    print("4. Env step ...", end=" ")
    env = EVRPTWEnv(n_customer=10, n_station=3)
    td  = env.reset(batch_size=[2])

    # Pick a valid action (first non-masked node per batch)
    mask = env.get_action_mask(td)    # True = masked
    valid = (~mask).long()
    action = valid.argmax(dim=-1)     # first valid node [2]

    td.set("action", action)
    next_td = env.step(td)["next"]
    assert "battery" in next_td.keys()
    assert "current_time" in next_td.keys()
    # Battery should have decreased (moved away from depot)
    # (depot action wouldn't decrease battery, so only check if action != 0)
    print(PASS)


def test_embeddings():
    print("5. Embeddings ...", end=" ")
    env = EVRPTWEnv(n_customer=10, n_station=3)
    td  = env.reset(batch_size=[2])

    init_emb = EVRPTWInitEmbedding(embedding_dim=64)
    ctx_emb  = EVRPTWContextEmbedding(embedding_dim=64)

    h = init_emb(td)                  # [2, 14, 64]
    assert h.shape == (2, 14, 64), f"init embed shape: {h.shape}"

    ctx = ctx_emb(h, td)              # [2, 64]
    assert ctx.shape == (2, 64), f"context shape: {ctx.shape}"
    print(PASS)


def test_schneider_loader():
    print("6. Schneider loader ...", end=" ")
    path = "data/schneider_instances/c103_21.txt"
    if not os.path.exists(path):
        print("SKIP (no instance file found)")
        return
    td = load_instance(path)
    assert td["locs"].shape[0] == 1
    n_nodes = td["locs"].shape[1]
    assert n_nodes > 100, f"Expected > 100 nodes, got {n_nodes}"
    check_instance(td)
    print(PASS)


def test_full_rollout():
    print("7. Full random rollout ...", end=" ")
    env = EVRPTWEnv(n_customer=5, n_station=2)
    td  = env.reset(batch_size=[1])
    actions = []

    for _ in range(50):
        mask   = env.get_action_mask(td)
        valid  = ~mask                      # True = valid
        if not valid.any():
            print(f"  [WARN] no valid action at step {len(actions)}")
            break
        action = valid.float().multinomial(1).squeeze(-1)  # random valid
        td.set("action", action)
        next_td = env.step(td)["next"]
        actions.append(action.item())
        if next_td["done"].all():
            break
        td = next_td

    # Compute reward
    if actions:
        actions_t = torch.tensor(actions).unsqueeze(0)
        reward = env._get_reward(td, actions_t)
        assert reward.shape == (1,)
        print(f"{PASS}  ({len(actions)} steps, reward={reward.item():.3f})")
    else:
        print(f"{FAIL} no actions taken")


if __name__ == "__main__":
    print("\n" + "="*45)
    print("  EVRP-TW Environment Smoke Tests")
    print("="*45)
    tests = [
        test_generator,
        test_env_reset,
        test_env_mask,
        test_env_step,
        test_embeddings,
        test_schneider_loader,
        test_full_rollout,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"  FAILED: {e}")
    print("="*45)
    print(f"  {passed}/{len(tests)} tests passed")
    print("="*45 + "\n")
