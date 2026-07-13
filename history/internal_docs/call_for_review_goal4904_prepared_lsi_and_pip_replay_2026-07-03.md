# Call For Review — Goal4904 Prepared LSI + PIP Hot Replay

Date: 2026-07-03

Please critically review Goal4904.

## Primary Report

- `history/internal_docs/goal4904_prepared_lsi_and_pip_replay_report_2026-07-03.md`

## Evidence

- `history/internal_docs/goal4904_prepared_lsi_pip_replay_summary_2026-07-03.json`
- `history/internal_docs/goal4903_buffered_writer_hot_session_summary_2026-07-03.json`

## Code Surface

- `history/internal_docs/goal4904_prepared_lsi_and_point_location_replay_probe.py`

## Requested Verdict Labels

- `approve_goal4904_prepared_lsi_pip_hot_replay`
- `approve_with_required_amendments`
- `block_due_to_metric_reframing`
- `block_due_to_correctness_or_semantics_risk`

## Questions

1. Does Goal4904 correctly use public prepared LSI query sessions and public prepared point-location sessions?
2. Does it preserve byte-for-byte output?
3. Is the hot-replay speedup correctly bounded to repeated-query/replay workloads?
4. Does the report avoid claiming single-run cold performance improvement?
5. Is the LSI replay improvement real and correctly measured (`1.814s` to `0.006s` in the hot replay comparison)?
6. Does the report correctly identify the remaining split: hot bottleneck is writer; cold/setup bottleneck is point-location base preparation?
7. Should Goal4904 close and authorize a next structural goal, not another trivial writer micro-tune?

## Non-Authorization Boundary

This review must not authorize:

- broad RTDL/RayJoin speedup claims;
- full eight-pair Section 5.7 claims;
- single-run speedup over AuthorOfficial;
- LSI/PIP semantic changes;
- hidden RayJoin-specific kernels;
- V3/V4 release resurrection;
- public release/tag decisions.
