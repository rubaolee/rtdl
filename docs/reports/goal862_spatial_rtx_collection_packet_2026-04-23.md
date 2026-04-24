# Goal862 Spatial RTX Collection Packet

Date: 2026-04-23

## Purpose

Goal862 packages the next real NVIDIA step for the two spatial prepared-summary
apps:

- `service_coverage_gaps`
- `event_hotspot_screening`

After Goal861, both apps are baseline-complete locally and blocked only on real
RTX artifact collection. This goal turns that state into a replayable packet
instead of leaving it as an informal note.

## Changed Files

- `/Users/rl2025/rtdl_python_only/scripts/goal862_spatial_rtx_collection_packet.py`
- `/Users/rl2025/rtdl_python_only/tests/goal862_spatial_rtx_collection_packet_test.py`

## What The Packet Contains

For each app, the packet records:

- current gate status from Goal860
- required local baselines and their artifact paths
- optional local SciPy baseline status
- exact deferred RTX command from Goal759
- exact expected RTX output artifact path
- claim scope and non-claim wording
- activation gate wording

It also emits a focused one-shot runner example:

```bash
python3 scripts/goal769_rtx_pod_one_shot.py \
  --only service_coverage_gaps \
  --only event_hotspot_screening \
  --include-deferred
```

## Boundary

This packet does not:

- collect the RTX artifacts itself
- promote either app automatically
- authorize a public speedup claim

It only packages the exact next RTX collection request now that the local
baseline side is complete.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal862_spatial_rtx_collection_packet_test \
  tests.goal860_spatial_partial_ready_gate_test \
  tests.goal859_spatial_summary_baseline_test
```

Result:

```text
Ran 11 tests
OK
```

Additional local checks:

```text
python3 -m py_compile \
  scripts/goal862_spatial_rtx_collection_packet.py \
  tests/goal862_spatial_rtx_collection_packet_test.py

git diff --check
```

Both passed.

## Verdict

Goal862 is complete locally. The next step for the spatial prepared-summary pair
is now a precise RTX collection run, not more local baseline or gate work.
