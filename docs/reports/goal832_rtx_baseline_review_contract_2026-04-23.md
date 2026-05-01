# Goal832 RTX Baseline Review Contract

Date: 2026-04-23

## Purpose

Goal832 adds explicit baseline-review contracts to the RTX cloud benchmark
manifest. This closes the gap identified in the NVIDIA RT-core WIP report:
RTX cloud artifacts prove selected prepared OptiX paths build and run, but a
public speedup claim still requires comparable baselines.

## Changed Files

- `/Users/rl2025/rtdl_python_only/scripts/goal759_rtx_cloud_benchmark_manifest.py`
- `/Users/rl2025/rtdl_python_only/tests/goal759_rtx_cloud_benchmark_manifest_test.py`

## Contract Added

Each active and deferred manifest entry now carries
`baseline_review_contract` with:

- `status: required_before_public_speedup_claim`
- `minimum_repeated_runs`
- `requires_correctness_parity`
- `requires_phase_separation`
- `forbidden_comparison`
- `comparable_metric_scope`
- `required_baselines`
- `required_phases`
- `claim_limit`

## Active Baseline Requirements

| Path | Required baseline family | Claim limit |
| --- | --- | --- |
| DB prepared compact summaries | CPU/oracle compact summary, Embree compact summary, PostgreSQL same semantics on Linux when available | Prepared DB sub-path only; not DBMS/SQL speedup. |
| Outlier prepared threshold count | CPU scalar threshold-count oracle, Embree scalar/summary path, SciPy/reference baseline when used | Threshold-count summary only; not row neighbors or full anomaly system. |
| DBSCAN prepared core count | CPU scalar core-count oracle, Embree scalar/summary path, SciPy/reference baseline when used | Core-count summary only; not full DBSCAN clustering. |
| Robot prepared pose count | CPU pose-count oracle, Embree any-hit pose-count or equivalent compact summary | Scalar pose-count only; not full planning, kinematics, CCD, or witness rows. |

## Deferred Baseline Requirements

The same manifest contract now also covers:

- service coverage prepared compact summary;
- event hotspot prepared compact summary;
- segment/polygon native hit-count gate.

These remain deferred. The baseline contract is a future review requirement,
not promotion into active RTX claim status.

## Boundaries

This goal does not start a cloud pod, does not run new performance tests, does
not authorize public speedup claims, and does not promote deferred apps. It
only makes future claim review stricter and more reproducible.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest -v tests.goal759_rtx_cloud_benchmark_manifest_test
```

Expected: all tests pass.

Actual local result:

```text
Ran 8 tests
OK
```

## Consensus

Goal832 has 2-AI consensus:

- Codex: `ACCEPT`
- Gemini 2.5 Flash: `ACCEPT`

Claude was attempted, but the CLI reported:

```text
You've hit your limit · resets 3pm (America/New_York)
```

Consensus ledger:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal832_two_ai_consensus_2026-04-23.md`

## Verdict

Goal832 is locally implemented and accepted by 2-AI consensus.
