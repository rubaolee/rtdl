# Goal3178: Point-Group Nearest-Witness Typed Producer Metadata

## Purpose

Goal3178 addresses the Hausdorff/X-HD v2.8 runtime-gap row after Goal3160/3161.
The exact partner front door already has generic naming, but the RT-core
nearest-witness device-column path did not yet present itself as a reusable
typed producer stream.

This goal adds app-agnostic typed producer metadata for the generic
`point_group_nearest_witness_2d` producer.

## What Changed

- Added `src/rtdsl/point_nearest_witness_typed_stream.py`.
- Added `make_v2_8_point_group_nearest_witness_typed_stream_contract(...)`.
- Added `make_v2_8_point_group_nearest_witness_typed_producer_metadata(...)`.
- Attached `typed_result_stream` and `v2_8_typed_producer_metadata` to
  `PreparedOptixPointGroupNearestWitness2D.write_device_nearest_witness_columns(...)`.
- Exported the helpers through `rtdsl.__init__`.
- Refreshed the Hausdorff/X-HD row in `v2_8_benchmark_runtime_gap.py`.

## Contract Shape

The producer is generic:

- primitive: `point_group_nearest_witness_2d`
- stream kind: `candidate_stream`
- columns: `query_id:uint32`, `neighbor_id:uint32`, `distance:float64`
- roles: `group_key`, `witness`, `score`
- ordering: stable query-row order

For non-empty OptiX launches into partner-owned CUDA output columns, the
metadata records device-resident output columns without host row materialization.
The report language is intentionally narrow: this is output-column residency
evidence for this producer, not a release claim.

This does not authorize true-zero-copy wording.

## Claim Boundary

Goal3178 authorizes no release, public speedup wording, broad RT-core wording,
whole-app speedup wording, true-zero-copy wording, hidden dispatch, hidden
partner selection, or app-specific native-engine behavior.

The important distinction is:

- solved: typed metadata for partner-owned CUDA output columns from the generic
  nearest-witness producer;
- still open: serious-scale device-resident continuation proof, broader partner
  conformance, prepared input residency, and end-to-end true-zero-copy evidence.

Required false flags include:

- `v2_8_release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`

## Local Validation

Passed:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3178_point_group_nearest_witness_typed_producer_metadata_test `
  tests.goal3161_v2_8_runtime_gap_hausdorff_generic_alias_refresh_test `
  tests.goal3143_hausdorff_partner_exact_numba_front_door_test
```

Result: 14 tests passed, 2 CUDA-gated tests skipped.

## Pod Validation

Passed on the active NVIDIA pod from a clean `origin/main` reset:

```bash
cd /root/rtdl_goal3151
git fetch origin main
git reset --hard origin/main
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
/root/venvs/rtdl_goal3154/bin/python -m unittest \
  tests.goal3178_point_group_nearest_witness_typed_producer_metadata_test \
  tests.goal3161_v2_8_runtime_gap_hausdorff_generic_alias_refresh_test \
  tests.goal3143_hausdorff_partner_exact_numba_front_door_test
```

Pod head: `324731ed`.

Result: 14 tests passed. The pod run exercised the Goal3143 CUDA/Numba path and
emitted only low-occupancy Numba warnings from tiny fixture sizes.

## Next Work

The next v2.8 step should move from metadata to execution evidence:

1. keep `point_group_nearest_witness_2d` as the producer contract;
2. preserve the explicit partner-choice rule;
3. show a same-stream or event-ordered continuation over the produced columns
   at serious benchmark scale;
4. record whether prepared source/target inputs stay resident or require host
   repacking; and
5. keep true-zero-copy and public speedup wording blocked until that evidence is
   reviewed.
