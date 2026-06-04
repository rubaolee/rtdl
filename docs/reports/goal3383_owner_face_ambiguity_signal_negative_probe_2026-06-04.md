# Goal3383 - Owner-Face Ambiguity Signal Negative Probe

Date: 2026-06-04

Verdict: reject-for-default-route.

## Purpose

Goal3381 showed that the selective owner-face CuPy continuation can repair the
full 512-chain county slice when the caller supplies the correct ambiguity set
and owner-face priorities.

Goal3383 asks the next question: can a simple generic topology signal discover
that ambiguity set without peeking at the known answer?

## Evidence

Pod: NVIDIA RTX A5000, driver 580.126.09

Source commit: `6779cdc9bee86745924593154371eef5816ce039`

Artifact:
`docs/reports/goal3383_owner_face_ambiguity_signal_negative_probe_2026-06-04.json`

The probe uses:

- live OptiX candidate device columns,
- a live exact OptiX run only as the evaluation oracle,
- CDB-derived topology rows,
- CDB-derived incident face rows.

The signal predicates themselves do not use the exact oracle.

## Result

True candidate-extra points:

```text
522, 523, 538, 539, 540, 564, 565
```

| Signal | Selected | True Positives | False Positives | Missed Extras | Default Candidate |
| --- | ---: | ---: | ---: | ---: | --- |
| `candidate_count_ge_3` | 407 | 7 | 400 | 0 | no |
| `candidate_count_gt_incident_max_face_count` | 47 | 5 | 42 | 2 | no |
| `incident_row_eq_3_candidate_ge_4` | 7 | 5 | 2 | 2 | no |
| `incident_row_eq_3_candidate_face_count_eq_4` | 9 | 7 | 2 | 0 | no |
| `incident_chain_count_eq_3_candidate_face_count_eq_4` | 9 | 7 | 2 | 0 | no |

The best compact signal is:

```text
incident_row_eq_3_candidate_face_count_eq_4
```

It selects all seven true extra points, but it also selects points 651 and 652.
Those two points are not errors: their live candidate rows already match exact
rows (`candidate_count=4`, `exact_count=4`, `extra_count=0`). Applying owner-face
repair to them as if they were erroneous would risk removing valid rows.

## Interpretation

This is a useful negative result. It prevents us from shipping a tempting but
wrong default route.

Simple topology-only candidate-count signals are not enough to decide when the
selective owner-face continuation should run. The runtime can already execute
the repair correctly when the caller supplies the ambiguity set, but RTDL does
not yet have a validated non-fixture ambiguity detector.

The likely next design target is a richer generic boundary-event or
same-stream classification primitive that can expose enough device/runtime
evidence for the caller to decide when owner-face repair is needed without
using an exact oracle.

## Boundary

This does not authorize a native default route. It rejects the tested simple
signal family for default routing.

This does not authorize release, public speedup, RayJoin paper reproduction,
RTDL-beats-RayJoin, RT-core speedup, or true-zero-copy claims. All artifact
claim-boundary flags remain false.
