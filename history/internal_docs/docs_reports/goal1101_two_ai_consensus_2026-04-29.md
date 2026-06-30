# Goal1101 Two-AI Consensus

Date: 2026-04-29

## Scope

Goal1101 adds replayable current-contract non-OptiX baseline tooling for the post-pod RTX rows identified by Goal1100:

- `facility_knn_assignment / coverage_threshold_prepared_recentered`
- `barnes_hut_force_app / node_coverage_prepared_rich`

## Consensus

| Reviewer | Verdict | Evidence |
| --- | --- | --- |
| Claude | ACCEPT with minor notes | `docs/reports/goal1101_claude_review_2026-04-29.md` |
| Codex | ACCEPT | `scripts/goal1101_current_contract_non_optix_baseline_profiler.py`, runner script, focused tests, and local smoke runs |

## Agreed Implementation

| Component | State |
| --- | --- |
| Baseline profiler | Supports `cpu_oracle` and `embree` for the current Facility and Barnes-Hut contracts. |
| Embree API usage | Uses `prepare_embree_fixed_radius_count_threshold_2d(...)`, `.run(...)`, and `.close()` in a `finally` block. |
| Runner | Emits four intended baseline artifacts: Facility CPU oracle, Facility Embree, Barnes-Hut validation Embree, Barnes-Hut 20M timing Embree. |
| Boundary | Every artifact carries `public_speedup_claim_authorized: false`; runner refuses to collect review-grade artifacts without a source commit. |

## Review Follow-Up

Claude noted minor test gaps. Codex addressed two immediately after the review:

- added a mocked Embree Facility test;
- added a `skip_validation=True` timing-row test.

The remaining note is cosmetic: `point_pack_sec` is `0.0` for Embree because Embree packing is internal to prepare/run. Consumers should treat it as no separate explicit packing phase for this profiler.

## Verification

Commands run:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal1101_current_contract_non_optix_baseline_profiler_test
bash -n scripts/goal1101_current_contract_non_optix_baseline_runner.sh
PYTHONPATH=src:. python3 scripts/goal1101_current_contract_non_optix_baseline_profiler.py --scenario facility_service_coverage_recentered --backend cpu_oracle --copies 1 --iterations 1 --radius 1.0 --output-json /tmp/goal1101_facility_smoke.json
PYTHONPATH=src:. python3 scripts/goal1101_current_contract_non_optix_baseline_profiler.py --scenario facility_service_coverage_recentered --backend embree --copies 1 --iterations 1 --radius 1.0 --output-json /tmp/goal1101_facility_embree_smoke.json
PYTHONPATH=src:. python3 scripts/goal1101_current_contract_non_optix_baseline_profiler.py --scenario barnes_hut_node_coverage --backend embree --body-count 8 --iterations 1 --radius 10.0 --barnes-tree-depth 1 --hit-threshold 1 --output-json /tmp/goal1101_barnes_embree_smoke.json
```

Results:

- Focused tests: 4 tests, OK
- Shell syntax: OK
- Facility CPU oracle smoke: `matches_oracle: true`
- Facility Embree smoke: `matches_oracle: true`
- Barnes-Hut Embree smoke: `matches_oracle: true`

## Boundary

Goal1101 does not authorize public RTX speedup claims. The generated artifacts still require artifact intake, same-current-contract comparison against RTX evidence, 2+ AI review, and public wording review before any README/front-page speedup language.
