# Phoenix V3 M52 POD Runner Authorization Surface Audit

Date: 2026-06-23

Status: `pod_runner_authorization_surface_audited_not_run_not_release`

M52 audits the current Phoenix V3 runner surface after M50/M51. The purpose is
to prevent old POD evidence scripts from being mistaken for current
authorization.

## Bottom Line

Current Phoenix V3 has only two fail-closed/token-gated executable surfaces in
the active path:

- `scripts/v3_phoenix_m47_librts_stability_protocol.py`
  - dry-run by default;
  - real run requires `--execute`;
  - real run also requires token `M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED`;
  - still not authorized until external review returns the exact run verdict.
- `scripts/v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner.py`
  - dry-run by default after M50;
  - real run requires `--execute`;
  - real run also requires token `M50_SPATIAL_TOPOLOGY_STREAM_M3_POD_AUTHORIZED`;
  - no current review authorizes using that token.

All older `v3_phoenix_*pod*` or focused evidence scripts without `--execute` and
an explicit token are historical evidence tooling unless a new review packet
re-authorizes and fail-closes them.

## Audit Findings

Fixed-string scan over `scripts/` and `tests/` found:

- `AUTHORIZATION_TOKEN` appears only in M47 and M50 active scripts;
- `--execute` appears in M47, M50, and a generic remote validation driver;
- many older POD-named scripts have no token gate and must not be treated as
  current executable authorization.

Saved scan evidence:

```text
docs/rebuild/v3/evidence/phoenix_v3_m52_pod_runner_authorization_surface_scan_20260623/summary.json
scan_name_filter: pod|remote|runner|stability_protocol
scanned_file_count: 126
token_gated_files:
- scripts/v3_phoenix_m47_librts_stability_protocol.py
- scripts/v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner.py
```

Representative historical direct-run scripts that remain non-current:

- `scripts/v3_phoenix_component_union_m38_pod_ab.py`
- `scripts/v3_phoenix_triangle_runner_m18_pod_ab.py`
- `scripts/v3_phoenix_rtdbscan_runner_m3_1_pod_ab.py`
- `scripts/v3_phoenix_rtdbscan_runner_m3_4_pod_ab.py`
- `scripts/v3_phoenix_rayjoin_point_location_runner_pod_ab.py`
- `scripts/v3_phoenix_barnes_hut_runner_parity_pod_ab.py`
- `scripts/v3_phoenix_aabb_prepare_reuse_pod_runner.py`
- `scripts/v3_phoenix_rtnn_prepared_execution_runner_repeat50_pod_ab.py`
- `scripts/v3_phoenix_rtnn_full_batch_float32_pod_evidence.py`
- `scripts/v3_phoenix_grouped_reduction_device_column_pod_evidence.py`

This audit does not delete or rewrite those scripts because they are part of
the historical evidence trail and tests may still inspect their payload
contracts. The current rule is stricter:

```text
Do not run historical POD scripts for current Phoenix V3 decisions unless a new
review packet first adds a dry-run/execute/token gate or an equally explicit
fail-closed runbook.
```

## Current Whitelist

| Surface | Current status | Can execute now? |
| --- | --- | --- |
| M47 LibRTS stability harness | fail-closed, token-gated | No; needs external verdict |
| M50 Spatial/RayJoin topology-stream runner | fail-closed, token-gated | No; no review authorizes token use |
| M38 component-union harness | historical single focused run consumed | No |
| M18 Triangle harness | historical focused run consumed | No |
| Other `v3_phoenix_*pod*` scripts | historical evidence tooling | No |

## Local Validation

Focused gate:

```text
PYTHONPATH=src;. py -3 -m unittest tests.v3_phoenix_m52_pod_surface_audit_gate_test tests.v3_phoenix_review_debt_and_completion_gate_test
Ran 5 tests
OK
```

Full V3 rebuild gate:

```text
PYTHONPATH=src;. py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 125
Ran 641 tests in 76.604s
OK
```

This is local contract/gate evidence only, not POD evidence.

## Required Rule For Future Reuse

If a historical POD script is needed again, do one of these before execution:

1. add M50-style `--execute` plus exact authorization token and dry-run default;
2. or create M51-style external-review runbook with dry-run-first and full
   copy-back requirements.

Then obtain external review before any paid run.

## Non-Authorization

M52 does not authorize:

- no V3 release
- no all-app benchmark run
- no paid POD spend
- no focused POD spend
- no public speedup wording
- no broad V3-over-V2 claim
- no V4 work
- no embedding
- no C ABI
- no true zero-copy claim

## Goal-Level Decision Audit

Decision: treat old POD runner scripts as historical tooling, not current
Phoenix V3 authorization, unless a new fail-closed review packet re-authorizes
them.

1. Was I foolish? No.
2. If yes, what actions made the decision foolish? The foolish action would be
   assuming a script name containing `pod` means it is safe to run today.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Audit the authorization surface and whitelist only token-gated current
   paths.
4. Can I now try a different path that actually solves the problem? Yes. Keep
   old evidence scripts readable, but require new fail-closed gates before any
   current paid execution.
