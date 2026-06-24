# Call For Review: Phoenix V3 M6 Barnes-Hut Evidence

Date: 2026-06-20

Reviewer: Claude or Gemini

## Request

Please critically review the Phoenix V3 M6 Barnes-Hut evidence update.

The goal is not to approve V3 release. The goal is to decide whether this
bounded M6 work can be accepted as internal route-parity evidence under the
Goal4392 V3 plan.

## Files To Review

Primary evidence and docs:

- `docs/rebuild/v3/phoenix_v3_m6_barnes_hut_pod_evidence_2026-06-20.md`
- `docs/rebuild/v3/evidence/phoenix_v3_m6_barnes_hut_20260620/m6_barnes_hut_intake_summary.json`
- `docs/rebuild/v3/evidence/phoenix_v3_m6_barnes_hut_20260620/m6_barnes_hut_intake_summary.md`
- `docs/rebuild/v3/evidence/phoenix_v3_m6_barnes_hut_20260620/m6_barnes_hut_partitioned.log`
- `docs/rebuild/v3/evidence/phoenix_v3_m6_barnes_hut_20260620/m6_barnes_hut_rerank.log`
- `docs/rebuild/v3/evidence/phoenix_v3_m6_barnes_hut_20260620/m6_barnes_hut_rerank_32768_65536_131072_partitioned_r11.json`

Supporting code and tests:

- `scripts/v3_phoenix_m6_barnes_hut_intake.py`
- `tests/v3_phoenix_m6_barnes_hut_intake_test.py`
- `tests/v3_phoenix_m6_barnes_hut_evidence_test.py`
- `scripts/run_test_matrix.py`

Status docs touched:

- `docs/rebuild/v3/README.md`
- `docs/rebuild/v3/v3_current_status_2026-06-20.md`
- `docs/rebuild/v3/phoenix_v3_m1_m7_compliance_table_2026-06-20.md`
- `docs/rebuild/v3/phoenix_v3_high_performance_candidate_matrix_2026-06-20.md`
- `docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md`

## Facts To Check

- The first single-process 32,768 / 65,536 / 131,072-body run failed with CUDA
  out-of-memory and is preserved as a negative artifact, not hidden.
- The successful run partitions by body count, then merges the JSON.
- Intake passed with:
  - `status: pass`
  - `overall_status: internal_m6_route_parity_evidence`
  - all release/public/RT-core speedup claim flags false
  - Phoenix M7-qualified release rows still 0
- The route matrix says fused Numba CUDA is fastest at 32,768 / 65,536 /
  131,072 bodies on this rerun.
- Prepared RTDL/OptiX+Numba is slower than fastest by 7.328x / 5.120x /
  13.912x on this rerun.
- The docs do not claim Barnes-Hut RT-core speedup, whole-app speedup, paper
  reproduction, automatic partner selection, or release authorization.

## Questions

1. Is this evidence honestly classified as internal M6 route-parity evidence?
2. Are the claim boundaries strong enough, especially around prepared OptiX
   losing to fused Numba CUDA?
3. Is the failed single-process OOM handled correctly?
4. Does the intake script enforce the right checks without overfitting to a
   desired result?
5. What P0/P1 changes are required before Codex can close this bounded M6 goal?

## Required Verdict Format

Please return:

- verdict: approve / approve-with-required-fixes / request-changes
- P0 findings
- P1 findings
- P2 suggestions
- final recommendation
