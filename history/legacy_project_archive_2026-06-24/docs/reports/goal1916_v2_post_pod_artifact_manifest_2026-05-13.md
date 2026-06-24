# Goal1916 - v2 Post-Pod Artifact Manifest

Status: pre-pod-ready

Date: 2026-05-13

## Scope

Goal1916 adds a reviewer-facing manifest generator for the Goal1903 v2 partner
RTX pod batch:

`scripts/goal1916_v2_post_pod_artifact_manifest.py`

Goal1905 answers "did the artifacts pass the strict acceptance gate?" Goal1916
answers "what exactly should reviewers read, from which source label, on which
GPU, and with which claim boundary?"

## Default Command

After the Goal1903 pod run and strict Goal1905 acceptance:

```bash
PYTHONPATH=src:. python3 scripts/goal1916_v2_post_pod_artifact_manifest.py
```

The visible-progress Goal1913 pod runbook also runs this command
automatically after strict Goal1905 acceptance.

Pre-pod dry snapshot:

```bash
PYTHONPATH=src:. python3 scripts/goal1916_v2_post_pod_artifact_manifest.py --allow-missing --output scratch/goal1916_pre_pod_manifest.json
```

## Manifest Contract

The manifest covers:

- `docs/reports/goal1903_fixed_radius_batch_pod.json`
- `docs/reports/goal1903_segment_polygon_batch_pod_512.json`
- `docs/reports/goal1903_segment_polygon_batch_pod_2048.json`
- `docs/reports/goal1889_road_hazard_prepared_reuse_pod_512.json`
- `docs/reports/goal1889_road_hazard_prepared_reuse_pod_2048.json`
- `docs/reports/goal1903_v2_partner_pod_batch_summary.json`

For each artifact it records:

- status and goal labels;
- GPU, git commit, and `source_commit_label` provenance;
- source-label agreement with the batch summary;
- partner names;
- count/result-count summary;
- claim-boundary status;
- review-readiness errors.

## Boundary

Goal1916 does not collect hardware evidence and does not authorize v2.0
release, broad RT-core speedup, or whole-app speedup claims. It is a packaging
and review aid for the post-pod evidence bundle.

The actual release remains blocked until RTX artifacts exist, Goal1905 passes
strictly, the Goal1916 manifest reports `pass`, and fresh external review plus
final release consensus are written.
