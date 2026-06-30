# Goal1170 External Review Request

Please review the clean-source RTX batch manifest/runner/intake implementation.

Files:

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

Local validation already run:

- `PYTHONPATH=src:. python3 scripts/goal1170_clean_source_rtx_batch_manifest.py`
- `PYTHONPATH=src:. python3 scripts/goal1171_clean_source_rtx_pod_preflight.py --dry-run`
- `PYTHONPATH=src:. python3 scripts/goal1172_clean_source_rtx_pod_runbook.py`
- `PYTHONPATH=src:. python3 -m unittest tests.goal1170_clean_source_rtx_batch_manifest_test tests.goal1171_clean_source_rtx_pod_preflight_test tests.goal1172_clean_source_rtx_pod_runbook_test -q`
- `git diff --check` on the Goal1170 files

Question:

Does Goal1170 correctly implement the pre-pod requirement from Goal1169?

Please verify:

- the manifest contains 8 rows: 6 not-yet-public-worded RTX-ready apps plus 2 clean replacement rows for ANN and robot;
- the runner refuses dirty git trees before collecting claim-grade artifacts;
- the runner invokes Goal1171 preflight before any benchmark row;
- the preflight verifies manifest shape, runner dirty-tree refusal, source cleanliness, NVIDIA/CUDA/NVCC/OptiX-library readiness, and GEOS readiness on real pod runs;
- `--skip-validation` appears only on the two large timing replacement rows;
- the intake rejects missing artifacts and dirty-source markers;
- the runbook gives a clean clone/build/preflight/batch/package flow and does not suggest copied dirty source;
- the files do not authorize public speedup wording by themselves;
- the batch structure avoids repeated pod start/stop cycles.

Write verdict to:

`docs/reports/goal1170_external_review_2026-04-30.md`

Use `VERDICT: ACCEPT` only if technically correct and conservative. Use
`VERDICT: BLOCK` with exact required fixes otherwise.
