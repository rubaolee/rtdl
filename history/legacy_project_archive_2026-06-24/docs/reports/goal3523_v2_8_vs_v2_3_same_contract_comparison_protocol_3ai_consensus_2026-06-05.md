# Goal3523 3-AI Consensus: v2.8 vs v2.3 Same-Contract Comparison Protocol

Date: 2026-06-05

Status: `accept-with-boundary`; protocol ready for pod execution, not final
performance results.

## Reviewed Files

- `src/rtdsl/v2_8_vs_v2_3_benchmark_comparison.py`
- `tests/goal3523_v2_8_vs_v2_3_same_contract_comparison_test.py`
- `docs/reports/goal3523_v2_8_vs_v2_3_same_contract_comparison_protocol_2026-06-05.md`
- `docs/reports/goal2654_all_benchmark_app_perf_comparison_refresh_2026-05-27.md`
- `docs/reports/goal3518_v2_8_benchmark_matrix_refresh_2026-06-05.md`
- `docs/reports/goal3521_v2_8_final_validation_packet_2026-06-05.md`
- `docs/release_reports/v2_3/README.md`

## Review Files

- Claude: `docs/reviews/goal3523_claude_review_v2_8_vs_v2_3_comparison_protocol_2026-06-05.md`
- Gemini initial review: `docs/reviews/goal3523_gemini_review_v2_8_vs_v2_3_comparison_protocol_2026-06-05.md`
- Gemini rereview after corrections: `docs/reviews/goal3523_gemini_rereview_v2_8_vs_v2_3_comparison_protocol_after_corrections_2026-06-05.md`

## Review Outcome

| Reviewer | Verdict | Outcome |
| --- | --- | --- |
| Codex | `accept-with-boundary` | Built the protocol, row map, report, and guard test. Existing artifacts are treated as triage only except explicitly bounded rows. |
| Claude | `accept-with-boundary` | Found one required correction: `contact_manifold` was wrongly treated as not promoted in the current v2.3 evidence baseline. Also requested RT-DBSCAN phase disclosure and RTNN uniform-row guidance. |
| Gemini | `accept-with-boundary` | Initial review accepted the protocol. A post-correction rereview confirmed the contact-manifold fix, RT-DBSCAN phase disclosure, and blocked claim boundaries. |

## Corrections Applied After Review

Claude's required correction was applied before this consensus:

- `contact_manifold` is now `v2_3_promoted=True` for the current v2.3 release-report/evidence baseline.
- `contact_manifold` is classified as `fresh_same_contract_pod_required`, not `v2_3_not_promoted`.
- `contact_manifold` records the Goal2654 v2.3-era OptiX timing `0.0184764`.
- The row and report disclose the historical drift: the literal `v2.3` tag text listed nine promoted apps, while the current v2.3 release report and Goal2654 evidence include contact manifold.

Claude's advisory fixes were also applied:

- `rt_dbscan` now states that the existing 5.36x internal estimate mixes a v2.3 total-run figure with a v2.8 grouped-stream tail median, so a same-phase pod rerun is required before final results.
- `rtnn` now instructs the pod run to lead with the uniform distribution because the existing v2.3 timing is a single uniform ranked-summary row.

## Validation

Focused local gate:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal3523_v2_8_vs_v2_3_same_contract_comparison_test \
  tests.goal3522_v2_8_internal_closeout_packet_test \
  tests.goal3518_v2_8_benchmark_matrix_test

Ran 17 tests in 0.009s
OK
```

Syntax check:

```text
py -3 -m py_compile \
  src/rtdsl/v2_8_vs_v2_3_benchmark_comparison.py \
  tests/goal3523_v2_8_vs_v2_3_same_contract_comparison_test.py
```

The forbidden-phrase scan over the Goal3523 report, source, and test returned no
matches for public release, public speedup, whole-app speedup, true-zero-copy,
package-install, or editable-install authorization wording.

## Consensus

Goal3523 is accepted as the protocol for the v2.8-vs-v2.3 all-benchmark
comparison.

It is ready for pod execution. It is not the final performance comparison
packet.

The final performance packet must:

- run on one hardware/toolchain profile;
- keep two clean workspaces for v2.3 and v2.8;
- report tag/current-report drift for contact manifold;
- split evolved contracts instead of collapsing them into one app ratio;
- separate setup, warmup, steady-state, and validation phases where available;
- preserve all claim-boundary blocks.

## Public Boundary

This consensus does not authorize:

- a public v2.8 release;
- public speedup wording;
- whole-app speedup wording;
- broad RT-core speedup wording;
- package-install or PyPI wording;
- true zero-copy wording;
- paper reproduction claims;
- hidden partner selection;
- app-specific native-engine behavior.
