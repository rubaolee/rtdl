# Goal5411 X-HD Bounded Statused Deferral Sample-Row Gate Result

Date: 2026-07-10

Status:

```text
bounded_xhd_statused_deferral_sample_row_gate_failed__sample_rows_not_recovered
```

## Purpose

Goal5410 proved that the existing generic active-query status machine can
express a synthetic app-neutral statused large-cell deferral stream.

Goal5411 applies that generic bridge to the real Goal5387 author sample source
ids and asks:

```text
Can the generic statused deferral stream recover the sampled author raw
source/cell rows without hard-coding the samples?
```

## Artifacts

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5411_bounded_statused_deferral_sample_row_gate.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5411_bounded_statused_deferral_sample_row_gate_pod.json
tests/goal5411_bounded_statused_deferral_sample_row_gate_test.py
```

## POD Execution

POD:

```text
POD_OK
hostname = 45c502cfccb5
GPU      = NVIDIA RTX 4000 Ada Generation, 550.127.05
```

POD focused unit:

```text
python3 -m unittest tests.goal5411_bounded_statused_deferral_sample_row_gate_test

Ran 4 tests OK (skipped=1)
```

POD real gate:

```text
PYTHONPATH=src python3 \
  Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5411_bounded_statused_deferral_sample_row_gate.py \
  --input1 /tmp/xhd_goal5234/data/dragon.ply \
  --input2 /tmp/xhd_goal5234/data/asian_dragon.ply
```

Result:

```text
status  = bounded_xhd_statused_deferral_sample_row_gate_failed__sample_rows_not_recovered
matched = true
```

`matched=true` here means the probe completed and claim-boundary checks are
well-formed. It does **not** mean the bounded X-HD author sample-row gate passed.

## Result

Generic bridge telemetry:

```text
active_query_count      = 3
candidate_row_count     = 168
offload_row_count       = 3
completed_row_count     = 0
miss_row_count          = 0
aborted_row_count       = 0
pruned rows             = 165
```

Author samples:

```text
source=11168,  author_cell=2924
source=210712, author_cell=17
source=437119, author_cell=17
```

Observed generic statused deferral rows:

```text
source=11168  -> [1554]
source=210712 -> [1554]
source=437119 -> [1554]
```

Membership:

```text
source=11168,  author_cell=2924, present=false
source=210712, author_cell=17,   present=false
source=437119, author_cell=17,   present=false
```

Decision:

```text
bounded_xhd_author_sample_row_gate_passed = false
full_goal5387_row_identity_gate_authorized = false
explicit_lb_support_authorized = false
direct_native_fix_authorized = false
recommended_next_goal = Goal5412_fail_close_explicit_lb_or_design_new_generic_native_trace_semantics
```

## Interpretation

Goal5411 is a no-go for the current generic statused bridge.

The synthetic app-neutral contract exists, but when applied to the real X-HD
sample sources through the current RTDL native frontier and generic status
bridge, it does not recover the author sampled raw rows.

This is stronger than Goal5408:

```text
Goal5408: compact/original cell namespace remap does not recover samples.
Goal5411: generic statused deferral over current RTDL frontier also does not
          recover samples.
```

The remaining gap now points to either:

```text
1. fail-close explicit -lb under the current RTDL execution model; or
2. design a new generic native traversal trace semantics that more directly
   matches author shader payload/offload behavior.
```

Option 2 must still be generic. It cannot be an X-HD-only patch or a hard-coded
sample-row fix.

## Validation

Local validation after artifact download:

```text
$env:PYTHONPATH='src'; py -m json.tool `
  Paper-reproduction-apps/x-hd-paper/results/xhd_goal5411_bounded_statused_deferral_sample_row_gate_pod.json

$env:PYTHONPATH='src'; py -m unittest `
  tests.goal5411_bounded_statused_deferral_sample_row_gate_test `
  tests.goal5410_statused_large_cell_deferral_stream_probe_test `
  tests.goal5409_status_machine_semantics_decision_test `
  tests.goal5408_cell_namespace_reconciliation_test `
  tests.goal5407_full_cover_delta_membership_probe_test

Ran 27 tests OK
```

## Claim Boundary

This goal proves:

```text
The current generic statused deferral bridge does not recover the sampled
Goal5387 author rows for the bounded source set.
```

This goal does not prove:

```text
explicit -lb support;
full Goal5387 row identity parity;
Figure 7 reproduction;
Figure 11 reproduction;
author performance parity;
exact paper dataset reproduction;
full X-HD paper reproduction.
```

## Recommended Next Step

```text
Goal5412_fail_close_explicit_lb_or_design_new_generic_native_trace_semantics
```

Goal5412 should be a decision gate:

```text
Branch A: fail-close explicit -lb for this release line, preserving scalar
          Level-B and generic system extraction.

Branch B: authorize a new generic native traversal trace semantic only if it
          can be specified without X-HD option names, paper figure semantics,
          hard-coded row fanout, or hard-coded sample rows.
```
