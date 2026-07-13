# Goal5506: LibRTS Scalable Semantics Gate

## Status

`implemented__scalable_same_input_probe__review_pending`

## Setup

The app generated a deterministic float32 probe with seed `5506`: 128
geometry boxes, 64 query boxes, and 8,192 pair evaluations. The probe includes
ordinary random boxes plus exact-box, shared-edge, one-ULP-gap, and shared-
corner cases. The same geometry/query files were passed to the author binary
and RTDL OptiX on the RTX 4000 Ada POD.

## Result

```text
CPU inclusive oracle  : 20
source RayParams model: 21
author GPU runtime     : 21
RTDL OptiX             : 20
```

The source-driven model matches the author runtime count. RTDL matches the
independent CPU inclusive count. The two execution contracts therefore remain
distinct on this 8,192-pair probe. This scales the Goal5505 observation beyond
one box and five queries, but it does not identify the cause of the two large
official-archive disagreements.

## Interpretation

The result is evidence for a contract difference, not a verdict that the
author is wrong or that RTDL is wrong. It does not justify copying the
RayParams diagonal shader into generic RTDL core. A future semantic change
would need a broader generic contract, relation-level evidence, and a
regression matrix that is not LibRTS-shaped.

Runtime phase fields are recorded separately. No author/RTDL performance ratio
is authorized.

## Claim Boundary

```json
{
  "scalable_probe_only": true,
  "full_input_adjudication": false,
  "full_input_root_cause_resolved": false,
  "rtdl_core_change_authorized": false,
  "author_specific_rtdl_core_behavior_authorized": false,
  "performance_ratio_authorized": false,
  "paper_reproduction_claimed": false,
  "embree_in_scope": false
}
```

Machine-readable evidence:

`Paper-reproduction-apps/librts-paper/results/goal5506_scalable_semantics_gate.json`
