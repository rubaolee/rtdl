# Goal3052 Partner Choice Pod Refresh

Date: 2026-06-02
Source commit tested on pod: `4cb8ce65255c6be8438e0a97ef69b2ea0c77a074`
GPU: NVIDIA RTX A4000

## Purpose

Goal3050 documented how users should choose CuPy or Numba for custom logic
after using RTDL primitives. Goal3052 keeps the pod evidence aligned with that
guidance by running a focused partner refresh on the live A4000 pod.

This is evidence for selected partner contracts, not a release authorization or
broad partner speedup claim.

## Environment Note

The pod checkout initially lacked `numba` in `/root/.venvs/rtdl_goal3042`, so
the first real Numba runner failed before executing kernels. The missing
partner stack was installed into that venv, then `numba.cuda.is_available()`
reported `True` on the NVIDIA RTX A4000. The rerun below is the valid evidence.

The venv install pulled `nvidia-nvjitlink-cu12 12.9.86`, while Torch in the
pod advertises a `12.8.93` pin. The focused Goal3052 Numba runners do not use
Torch, but future Torch/Triton runs on this pod should re-check that toolchain
before using the same venv for Torch evidence.

## Artifacts

Artifacts are stored under:

```text
docs/reports/goal3052_partner_choice_pod_refresh_2026-06-02/
```

| Artifact | Workload | Result |
| --- | --- | --- |
| `raydb_numba_minmax_1m.json` | RayDB-style Numba count/sum/min/max/avg continuation over 1,000,000 rows and 4096 groups | pass |
| `triangle_numba_compact_mask_1m.json` | Triangle-counting compact-mask continuation over 1,000,000 rows | pass |
| `rayjoin_numba_compact_mask_1m.json` | RayJoin compact-mask continuation for `pip`, `lsi`, and `overlay_seed` over 1,000,000 rows each | pass |
| `grouped_arg_reducer_1m.json` | Generic grouped argmin/argmax reducer, including 1,000,000-row large stream and tie fixture | pass |
| `hausdorff_active_frontier_small_refresh.json` | Small Hausdorff active-frontier vs CuPy grouped-grid timing refresh over two dataset shapes and two sizes | exact distances match |

## Timing And Correctness Highlights

| Path | Correctness | Timing note |
| --- | --- | --- |
| RayDB Numba min/max | all five modes matched CPU NumPy reference | runner elapsed 1.184756 s |
| Triangle compact mask | candidates, original indices, and partner mask indices matched CPU | runner elapsed 0.981128 s |
| RayJoin compact mask | all three workloads matched CPU | runner elapsed 1.627693 s |
| Grouped arg reducer | tie fixture and 1M-row large stream matched CPU for argmin and argmax | large-stream argmin wall 0.178572 s; argmax wall 0.185973 s |
| Hausdorff active frontier | all rows matched CuPy grouped-grid exact distance | median speedup vs CuPy: min 2.142701x, median 3.025957x, max 4.470931x |

## Claim Boundary

These runs support the current partner-choice documentation:

- Numba is a real selectable custom-kernel partner for selected generic
  continuations.
- CuPy remains a strong baseline and is still the right recommendation for rows
  where it has the measured reference role.
- RTDL primitive-first remains the recommended path when a fused primitive
  exactly expresses the answer.

These runs do not authorize:

- v2.6 release;
- package-install claims;
- broad RT-core speedup claims;
- broad CuPy or Numba acceleration claims;
- automatic partner selection;
- whole-application speedup claims.
