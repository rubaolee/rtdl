# Goal1914 - v2 Pod Artifact Provenance Hardening

Status: local-preflight-pass

Date: 2026-05-13

## Scope

Goal1914 hardens the Goal1903 / Goal1905 pod path so RTX evidence cannot be
accepted from stale, mixed-source, or non-RTX artifacts.

The change is deliberately narrow:

- `scripts/goal1878_fixed_radius_app_adapter_perf.py` now writes top-level
  `git_commit`, `source_commit_label`, and `gpu` fields.
- `scripts/goal1863_segment_polygon_hitcount_v2_partner_perf.py` now writes a
  top-level `source_commit_label`, matching the existing commit and GPU fields.
- `scripts/goal1903_v2_partner_pod_batch_runner.sh` rejects fixed-radius and
  segment/polygon artifacts that do not contain RTX GPU provenance, a git
  commit, and the same `source_commit_label` as the batch summary.
- `scripts/goal1905_v2_partner_pod_batch_acceptance.py` applies the same
  provenance checks across fixed-radius, segment/polygon, and road-hazard
  artifacts.

## Why This Matters

Before this hardening, Goal1903 already refused to start accepted runs on a
non-RTX GPU, and road-hazard artifacts already recorded commit/source/GPU
metadata. The fixed-radius artifact did not record those fields, and the final
acceptance validator did not independently reject mixed-source artifacts.

That was too easy to misread during a long pod session. Goal1914 makes the
post-pod path fail closed:

- a GTX/local artifact cannot pass as accepted RTX evidence;
- a copied artifact from a different source checkout cannot silently mix into
  the batch;
- missing commit/GPU metadata is a structural failure, not a manual review
  footnote.

## Boundary

Goal1914 does not collect pod timings and does not authorize v2.0 release. It
only strengthens the evidence contract for the next pod run.

Accepted v2.0 release remains blocked until:

- Goal1903 artifacts are produced on an RTX pod;
- Goal1905 passes in strict mode on those artifacts;
- a fresh Claude or Pro-class review examines the actual post-pod artifacts;
- final source-tree/package and v2.0 release consensus are written.

## Local Validation

Codex ran:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal1878_fixed_radius_app_adapter_perf_test tests.goal1863_segment_polygon_hitcount_v2_partner_perf_test tests.goal1903_v2_partner_pod_batch_packet_test tests.goal1905_v2_partner_pod_batch_acceptance_test
$env:PYTHONPATH='src;.'; py -3 scripts\goal1908_v2_local_preflight.py --output scratch\goal1908_after_provenance.json
```

Both passed. Goal1908 remains a non-pod preflight; its readiness snapshot still
correctly reports v2.0 as blocked on missing RTX pod artifacts and final
reviews.
