# V4 Tier-3 Numba PTX Spike

Status: V4.x spike evidence, not V4.0 support and not a release announcement

Tier 3 is for scalar per-hit user reduce logic that cannot be represented by a
measured Tier-2 fused operator. The intended path is:

1. user writes a constrained Numba device function
2. RTDL compiles it to PTX
3. a future OptiX traversal shell links that PTX as a callable/module
4. the linked route is measured for correctness and overhead

Only step 2 is probed here.

## Probe

Run locally without CUDA:

```bash
python scripts/v4_tier3_numba_ptx_probe.py --dry-run
```

Run on a CUDA evidence environment:

```bash
python scripts/v4_tier3_numba_ptx_probe.py \
  --json-out future/v4/evidence/v4_tier3_numba_ptx_probe_2026-06-24.json \
  --md-out future/v4/evidence/v4_tier3_numba_ptx_probe_2026-06-24.md
```

Passing this probe means only that a scalar Numba device callback can generate
PTX in the current toolchain. It does not mean that OptiX accepts the PTX, that
callable overhead is acceptable, or that Tier-3 is a public V4.0 feature.

## Non-Claims

This page does not authorize:

- V4 release
- Tier-3 callback/PTX support claims
- raw OptiX callback support
- broad speedup wording
- whole-application speedup wording
- app-specific native engine kernels

