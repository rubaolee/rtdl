# Phoenix V3 M43 Grouped Reduction CuPy Warp Prepared Runner

Date: 2026-06-23

Status: `m43_original_shape_cpu_hot_inversion_cleared_not_release`

This report records the M43 local-only grouped-reduction fix after M42 showed that the original M41 shape failed because the Numba offsets kernel exposed too little parallelism.

This is not a release authorization, not an all-app authorization, not paid-POD authorization, not public speedup wording, not V4, not embedding, not C ABI, and not true-zero-copy evidence.

## What Changed

M43 added two generic runtime capabilities:

1. Numba grouped-vector offsets auto strategy:
   - `thread_per_group_serial` for high-group-count / low-rows-per-group shapes
   - `warp_per_group_tiled` for lower-group-count / high-rows-per-group shapes

2. CuPy prepared grouped-vector offsets session:
   - `partner='cupy'` is now accepted by `prepare_grouped_vector_sum_2d_partner_columns_session`
   - `run_grouped_vector_sum_2d_prepared_session` now accepts explicit partner `cupy`
   - CuPy RawKernel uses warp-per-group row-parallel reduction when `rows_per_group_mean >= 32`
   - launch metadata is reported through the productized prepared-session runner

The added CuPy kernel is generic grouped-reduction runtime work. It is not an app route.

## Local Validation

Local Windows checks:

```text
PYTHONPATH=src;. py -3 -m py_compile \
  src/rtdsl/partner_adapters.py \
  src/rtdsl/prepared_execution.py \
  src/rtdsl/numba_partner_continuation.py \
  scripts/v3_phoenix_grouped_reduction_m41_local_harness.py

PYTHONPATH=src;. py -3 -m unittest tests.v3_phoenix_m41_grouped_reduction_harness_test
7 tests OK

PYTHONPATH=src;. py -3 -m unittest tests.v3_phoenix_prepared_execution_session_runner_test -k grouped_vector_sum
3 tests OK
```

Full V3 rebuild matrix after the trusted-offset follow-up:

```text
docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m43_trust_offsets_followup_20260623_154700.json
120 modules / 627 tests OK
```

## Diagnostic Attempts

All runs were free local lx1 runs, not paid POD.

| Route | Evidence | runner vs CPU hot | Interpretation |
|---|---|---:|---|
| Numba block-per-group tiled | `docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m43_lx1_tiled_original_262144x1024_20260623_152926/` | `0.6216966017370773x` | Correct but still CPU-slower |
| Numba warp-per-group tiled | `docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m43_lx1_warp_tiled_original_262144x1024_20260623_153126/` | `0.6777200472439239x` | Improved but still CPU-slower |
| CuPy RawKernel warp prepared runner | `docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m43_lx1_cupy_warp_original_262144x1024_20260623_153707/` | `3.454249350723889x` | Original CPU-hot inversion cleared |
| CuPy RawKernel warp prepared runner, prevalidated offsets | `docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m43_lx1_cupy_warp_trust_offsets_262144x1024_20260623_154342/` | `3.634392783864349x` | Hot gate remains clear; wall caveat cleared for explicit trusted-offset mode |

The Numba path improved the original blocked shape but did not clear the CPU-hot gate. A direct CuPy RawKernel prototype showed that the kernel shape itself could run at about `0.000033s`; productizing that route through the prepared runner cleared the gate.

## M43 Main Evidence

Command:

```text
PYTHONPATH=src:. python3 scripts/v3_phoenix_grouped_reduction_m41_local_harness.py \
  --variant all \
  --partner cupy \
  --row-count 262144 \
  --group-count 1024 \
  --seed 20260623 \
  --warmup 2 \
  --repeat 5
```

Evidence:

```text
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m43_lx1_cupy_warp_original_262144x1024_20260623_153707/
```

Key result:

| Metric | Value |
|---|---:|
| failed checks | `0` |
| correctness | `allclose=true` |
| step2 local runner contract candidate | `true` |
| actual output partner | `cupy` |
| runtime trunk executes end-to-end | `true` |
| internal device residency between RTDL phases | `true` |
| hot-path host materialization | `false` |
| kernel strategy | `warp_per_group_tiled` |
| program count | `128` |
| groups per block | `8` |
| threads per group | `32` |
| rows per group mean | `256.0` |
| CPU hot median | `0.00016815285198390484 s` |
| legacy CuPy one-shot hot median | `0.00032473402097821236 s` |
| productized runner hot median | `0.00004867999814450741 s` |
| runner vs CPU hot | `3.454249350723889x` |
| runner vs legacy hot | `6.670789510185146x` |
| runner vs legacy wall | `0.8786019925331072x` |

## Interpretation

M43 clears the specific CPU-hot inversion that blocked grouped reduction on the original M41 shape (`262144` rows / `1024` groups). The fix is not an app-specific optimization: it adds a generic CuPy prepared-session route for grouped vector sums and records launch-shape metadata through the productized runner.

However, this is not a release result. The runner still loses to legacy CuPy one-shot on inclusive wall in this local run (`0.8786x`). That means the result is a strong hot-path/runtime-trunk signal, not an all-app or release-performance proof.

## Wall Follow-Up

The first CuPy prepared-session run showed that almost all inclusive runner wall time was in `prepare_sec=0.08580490993335843s`, not in the hot executor. M43 found and fixed a generic API bug: the CuPy prepared-session branch ignored the `validate_row_offsets` flag and always performed host-sync row-offset validation at prepare time.

M43 added explicit harness support for:

```text
--trust-row-offsets
```

This mode is only for caller/generated data whose row offsets are already trusted. It is explicit, not hidden automatic behavior.

Follow-up command:

```text
PYTHONPATH=src:. python3 scripts/v3_phoenix_grouped_reduction_m41_local_harness.py \
  --variant all \
  --partner cupy \
  --trust-row-offsets \
  --row-count 262144 \
  --group-count 1024 \
  --seed 20260623 \
  --warmup 2 \
  --repeat 5
```

Evidence:

```text
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m43_lx1_cupy_warp_trust_offsets_262144x1024_20260623_154342/
```

Key result:

| Metric | Value |
|---|---:|
| failed checks | `0` |
| correctness | `allclose=true` |
| runner vs CPU hot | `3.634392783864349x` |
| runner vs legacy hot | `3.3163301846618403x` |
| runner vs legacy wall | `15.409127696720203x` |

This does not authorize public claims. It does show that the earlier inclusive-wall regression was prepare validation overhead, not a hot-path failure.

## Non-Authorization

This report does not authorize:

- V3 release
- all-app benchmark run
- paid POD spend
- public speedup wording
- broad V3-over-V2 claim
- V4 work
- embedding
- C ABI
- true zero-copy claim

## Goal-Level Decision Audit

Decision: redirect from Numba-only tiled kernel work to productized CuPy warp RawKernel prepared-session support after Numba diagnostics failed to clear the CPU-hot gate, then add explicit trusted-offset mode after prepare validation dominated wall time.

1. Was I foolish? No.
2. If yes, what actions made the decision foolish? The foolish action would have been to keep forcing Numba after block-per-group, warp-per-group, and atomic diagnostics all remained CPU-slower.
3. Was there another path that would avoid being stuck? Yes. Either switch Step-2 family or test a lower-overhead CuPy RawKernel route. The CuPy prototype proved the route could clear the hot gate.
4. Can I now try a different path that actually solves the problem? Yes. M43 productized the CuPy route through the same prepared runner, cleared the original CPU-hot inversion locally, and showed the wall caveat clears when row offsets are explicitly trusted. The next step is external review, not paid POD or release.
