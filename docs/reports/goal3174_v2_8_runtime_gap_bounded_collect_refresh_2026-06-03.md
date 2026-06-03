# Goal3174 - v2.8 Runtime-Gap Refresh After Direct Bounded-Collect Front Door

Date: 2026-06-03

Status: local and pod validation complete.

## Purpose

Goal3173 added `execute_bounded_collect_typed_stream_partner_columns(...)`.
Goal3174 updates the v2.8 benchmark runtime-gap matrix for Robot collision and
Contact manifold so those rows no longer imply the bounded-output continuation
contract itself is missing.

## Matrix Changes

### Robot collision

Current best path now records the generic any-hit/collision flag primitive over
prepared static scenes plus the direct bounded-collect typed-stream front door
for optional grouped witness rows.

Remaining bottleneck is not the bounded-collect front door. It is native typed flag/witness producer evidence, prepared-scene residency metadata, and
same-scale optional witness benchmarks.

### Contact manifold

Current best path now records bounded witness collection with fail-closed
overflow behavior plus the direct bounded-collect typed-stream front door over
grouped item rows.

Remaining bottleneck is not the bounded-collect front door. It is native typed bounded-witness producer evidence, device-residency proof, and same-scale
partner/native benchmarks.

## Boundary

This refresh does not authorize release packaging, public speedup wording,
broad RT-core claims, true-zero-copy wording, automatic partner selection, or
app-specific native-engine behavior.

The matrix continues to enforce:

- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`

## Validation

Focused local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3174_v2_8_runtime_gap_bounded_collect_refresh_test `
  tests.goal3105_v2_8_benchmark_runtime_gap_map_test
```

Result: 8 tests passed locally.

Focused pod validation:

```bash
cd /root/rtdl_goal3151
git fetch origin main
git reset --hard origin/main
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
  /root/venvs/rtdl_goal3154/bin/python -m unittest \
  tests.goal3174_v2_8_runtime_gap_bounded_collect_refresh_test \
  tests.goal3105_v2_8_benchmark_runtime_gap_map_test
```

Pod result: commit `f76b88b1`, 8 tests passed.
