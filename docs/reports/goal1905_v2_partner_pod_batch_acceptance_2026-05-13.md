# Goal1905 - v2 Partner Pod Batch Acceptance Validator

Status: pre-pod-ready

Date: 2026-05-13

## Scope

Goal1905 adds a local acceptance validator for the Goal1903 pod batch artifacts:

`scripts/goal1905_v2_partner_pod_batch_acceptance.py`

The validator is meant to run immediately after the Goal1903 RTX pod batch. It
does not collect timing evidence and does not authorize v2.0 release. It only
checks that the expected artifacts exist, pass their local parity/status gates,
record consistent RTX/source provenance, and keep release and broad-speedup
claims blocked.

## Default Command

```bash
PYTHONPATH=src:. python3 scripts/goal1905_v2_partner_pod_batch_acceptance.py
```

The default expected artifacts are:

- `docs/reports/goal1903_fixed_radius_batch_pod.json`
- `docs/reports/goal1903_segment_polygon_batch_pod_512.json`
- `docs/reports/goal1903_segment_polygon_batch_pod_2048.json`
- `docs/reports/goal1889_road_hazard_prepared_reuse_pod_512.json`
- `docs/reports/goal1889_road_hazard_prepared_reuse_pod_2048.json`
- `docs/reports/goal1903_v2_partner_pod_batch_summary.json`

## Fail-Closed Checks

The validator fails if:

- any required artifact is missing, unless `--allow-missing` is used for a
  pre-pod board snapshot;
- any timing artifact lacks RTX GPU provenance, a git commit, or the same
  `source_commit_label` as the batch summary;
- fixed-radius status is not `measurement` or has empty results;
- segment/polygon status is not `pass`, strict count parity is false, or the
  same-contract timing row flag is missing;
- road-hazard status is not `pass`, the Goal1889 extension label is missing,
  strict priority parity is false, or prepared scene/output reuse is missing;
- any artifact sets `v2_0_release_authorized`,
  `whole_app_speedup_claim_authorized`, or
  `broad_rt_core_speedup_claim_authorized` to true.

In `--allow-missing` mode, stale partial Goal1903 summary request flags are
reported as warnings while the validator stays in `blocked_missing_artifacts`.
Strict post-pod mode still fails them.

## Boundary

Passing Goal1905 means the batch artifacts are structurally usable for review.
It does not replace external review, final release consensus, or exact public
claim selection.

## Local Linux Check

Codex copied the Goal1905 validator into the disposable local Linux checkout at
`/tmp/rtdl_goal1889_smoke` on `192.168.1.20` and ran:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal1905_v2_partner_pod_batch_acceptance_test
PYTHONPATH=src:. python3 scripts/goal1905_v2_partner_pod_batch_acceptance.py --allow-missing --output /tmp/goal1905_local_snapshot.json
```

Result: tests passed, and the pre-pod snapshot reported
`blocked_missing_artifacts` with no errors. The disposable checkout had a stale
partial Goal1903 summary from an earlier dry run, so the missing fixed-radius
and segment/polygon request flags were reported as warnings, as intended for
`--allow-missing` mode.
