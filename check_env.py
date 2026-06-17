"""
Environment check script for EVRP-TW project.
Run with: conda activate evrptw && python check_env.py
"""

import sys
import importlib

REQUIRED = [
    ("torch",        "PyTorch"),
    ("rl4co",        "RL4CO"),
    ("pyvrp",        "PyVRP"),
    ("numpy",        "NumPy"),
    ("pandas",       "pandas"),
    ("matplotlib",   "Matplotlib"),
    ("tensorboard",  "TensorBoard"),
    ("lightning",    "Lightning (pytorch-lightning)"),
]

print(f"\n{'='*55}")
print(f"  Python : {sys.version.split()[0]}")
print(f"  Prefix : {sys.prefix}")
print(f"{'='*55}")
print(f"  {'Package':<28} {'Status':<12} Version")
print(f"  {'-'*28} {'-'*12} -------")

all_ok = True
for mod, label in REQUIRED:
    try:
        m = importlib.import_module(mod)
        ver = getattr(m, "__version__", "?")
        print(f"  {'✓  ' + label:<31} {'OK':<12} {ver}")
    except ImportError:
        print(f"  {'✗  ' + label:<31} MISSING")
        all_ok = False

# PyTorch extras
print(f"\n  --- PyTorch details ---")
try:
    import torch
    print(f"  CUDA available : {torch.cuda.is_available()}")
    print(f"  MPS  available : {torch.backends.mps.is_available()}")
    device = "mps" if torch.backends.mps.is_available() else \
             "cuda" if torch.cuda.is_available() else "cpu"
    print(f"  Will train on  : {device}")
except ImportError:
    print("  (PyTorch not installed)")

print(f"\n{'='*55}")
if all_ok:
    print("  ✓  All required packages are installed.")
else:
    print("  ✗  Some packages are missing — see above.")
print(f"{'='*55}\n")
