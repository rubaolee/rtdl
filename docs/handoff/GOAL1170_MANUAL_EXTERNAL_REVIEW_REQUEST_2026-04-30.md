# Manual External Review Request: Goal1170

Please give this to Gemini or Claude manually if local CLI review remains unavailable.

Working directory:

`/Users/rl2025/rtdl_python_only`

Review:

- `docs/handoff/GOAL1170_EXTERNAL_REVIEW_REQUEST_2026-04-30.md`
- `scripts/goal1170_clean_source_rtx_batch_manifest.py`
- `scripts/goal1170_clean_source_rtx_batch_runner.sh`
- `scripts/goal1170_clean_source_rtx_batch_intake.py`
- `scripts/goal1171_clean_source_rtx_pod_preflight.py`
- `scripts/goal1172_clean_source_rtx_pod_runbook.py`
- `tests/goal1170_clean_source_rtx_batch_manifest_test.py`
- `tests/goal1171_clean_source_rtx_pod_preflight_test.py`
- `tests/goal1172_clean_source_rtx_pod_runbook_test.py`
- `docs/reports/goal1170_clean_source_rtx_batch_manifest_2026-04-30.json`
- `docs/reports/goal1170_clean_source_rtx_batch_manifest_2026-04-30.md`
- `docs/reports/goal1171_clean_source_rtx_pod_preflight_2026-04-30.json`
- `docs/reports/goal1171_clean_source_rtx_pod_preflight_2026-04-30.md`
- `docs/reports/goal1172_clean_source_rtx_pod_runbook_2026-04-30.json`
- `docs/reports/goal1172_clean_source_rtx_pod_runbook_2026-04-30.md`
- `docs/reports/goal1169_clean_source_rtx_claim_grade_batch_plan_2026-04-30.md`

Question:

Does Goal1170 correctly implement the pre-pod requirement from Goal1169?

Required checks:

- manifest has 8 rows: 6 `public_wording_not_reviewed` rows and 2 clean replacement rows;
- runner refuses dirty git trees before claim-grade collection;
- runner invokes Goal1171 preflight before app rows;
- preflight checks clean source and NVIDIA/CUDA/NVCC/OptiX-library/GEOS readiness for real pod runs;
- `--skip-validation` is limited to the two large timing replacement rows;
- intake rejects missing artifacts and dirty-source markers;
- runbook gives a clean clone/build/preflight/batch/package flow and does not suggest copied dirty source;
- no public RTX speedup wording is authorized by these files;
- batch structure avoids per-app cloud start/stop cycles.

Please write:

`docs/reports/goal1170_manual_external_review_2026-04-30.md`

Use `VERDICT: ACCEPT` only if correct and conservative. Use `VERDICT: BLOCK`
with exact required fixes otherwise.
