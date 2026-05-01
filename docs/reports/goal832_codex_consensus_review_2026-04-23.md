# Goal832 Codex Consensus Review

Date: 2026-04-23

Reviewer: Codex

## Scope

This review checks whether Goal832 adds baseline-review contracts to the RTX
cloud benchmark manifest without creating a performance claim or changing the
active/deferred app boundary.

## Findings

- Active RTX manifest entries now include `baseline_review_contract`.
- Deferred manifest entries also include the same contract, but remain
  deferred and are not promoted.
- The contract blocks invalid comparisons between scalar/prepared RTX
  sub-paths and whole-app, row-output, validation-included, or
  different-result-mode baselines.
- App-specific baseline families are explicit for DB, fixed-radius
  Outlier/DBSCAN summaries, robot pose-count summaries, service/hotspot
  deferred summaries, and segment/polygon native-gate evidence.
- The report states that Goal832 does not start cloud, run performance tests,
  authorize public speedup claims, or promote deferred apps.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest -v tests.goal759_rtx_cloud_benchmark_manifest_test
```

Result: `Ran 8 tests ... OK`.

```text
PYTHONPATH=src:. python3 scripts/goal759_rtx_cloud_benchmark_manifest.py --output-json /tmp/goal832_manifest_check.json
```

Result: manifest emitted `5` active entries and `3` deferred entries with
baseline-review contracts.

## Verdict

ACCEPT
