# Goal1168 Goal1166 Live Pod Intake Audit

Artifact dir: `/Users/rl2025/rtdl_python_only/docs/reports/goal1166_live_rtx_pod_2026-04-30`

- valid: `True`
- engineering verdict: `accept`
- claim-grade verdict: `blocked`

## Checks

| Check | Result |
| --- | --- |
| `all_expected_files_present` | `True` |
| `single_source_marker` | `True` |
| `source_marked_local_dirty` | `True` |
| `intake_records_engineering_accept_claim_block` | `True` |
| `source_context_records_dirty_tree` | `True` |
| `ann_validation_matches_oracle` | `True` |
| `ann_large_timing_validation_skipped` | `True` |
| `ann_large_timing_query_under_prior_timeout` | `True` |
| `robot_validation_matches_oracle` | `True` |
| `robot_timing_validation_skipped` | `True` |
| `robot_timing_query_under_prior_timeout` | `True` |
| `jaccard_chunk512_passed` | `True` |
| `jaccard_chunk256_diagnostic_failed` | `True` |

## Claim-Grade Blockers

- source tree was copied from a dirty local working tree
- ANN large row skipped validation and is timing-only
- robot large row skipped validation and is timing-only
- Jaccard chunk256 remains an expected diagnostic failure

## Boundary

This audit validates the copied Goal1166 live RTX pod artifacts as engineering evidence only. It does not authorize public speedup wording or claim-grade release evidence.
