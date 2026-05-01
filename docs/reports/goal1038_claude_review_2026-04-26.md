# Goal1038 Claude Review

Date: 2026-04-26
Reviewer: Claude (claude-sonnet-4-6)

## Verdict: ACCEPT

## Checklist

| Criterion | Result |
|---|---|
| Narrow packet — targets only four baseline-ready apps | PASS |
| Excluded non-ready apps (`prepared_pose_flags`, `graph_visibility_edges_gate`) | PASS |
| References Goal1036 corrected local evidence | PASS |
| Cites `goal1036_all_ready_apps_20000_after_outlier_fix_2026-04-26.md` | PASS |
| Confirms all 12 CPU/Embree/SciPy rows passed at `copies=20000` | PASS |
| No-single-app-pod rule preserved | PASS |
| Copy-back rule preserved (6 artifacts listed) | PASS |
| Does not authorize public speedup claims | PASS |
| Does not authorize NVIDIA RT-core superiority wording | PASS |
| Requires phase separation + repeated runs before any comparison | PASS |

## Test Results

All 3 automated tests in `tests/goal1038_next_rtx_ready_app_rerun_packet_test.py` passed:

- `test_packet_targets_only_four_baseline_ready_apps` — ok
- `test_packet_references_corrected_local_baseline_evidence` — ok
- `test_packet_preserves_cost_and_claim_boundaries` — ok

## Notes

The packet is correctly scoped. It restricts the next RTX pod run to exactly the four apps whose local CPU/Embree/SciPy baselines are confirmed correct after the Goal1036 oracle fix (`outlier_detection`, `dbscan_clustering`, `service_coverage_gaps`, `event_hotspot_screening`). The claim boundary section is explicit and complete: refreshed RTX artifacts are internal planning evidence only until same-hardware-class, phase-separation, repeated-runs, correctness-parity, and public-wording reviews are satisfied.
