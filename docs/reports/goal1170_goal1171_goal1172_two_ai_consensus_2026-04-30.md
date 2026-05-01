# Goal1170-Goal1172 Two-AI Consensus

Date: 2026-04-30

## Verdict

ACCEPT.

Goal1170, Goal1171, and Goal1172 are closed under the project 2-AI rule by
Codex plus Gemini.

## Scope

- Goal1170: clean-source RTX batch manifest, runner, and artifact intake.
- Goal1171: clean-source RTX pod preflight.
- Goal1172: clean-source RTX pod execution runbook.

## Reviewed Artifacts

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

## External Review

Gemini review:

- `docs/reports/goal1170_external_review_2026-04-30.md`
- Verdict: `ACCEPT`

Gemini confirmed:

- the manifest has 8 rows: 6 not-yet-public-worded RTX-ready apps plus 2 clean replacement rows;
- the runner refuses dirty git trees;
- the runner invokes Goal1171 preflight before benchmark rows;
- the preflight checks manifest shape, dirty-tree refusal, source cleanliness, NVIDIA/CUDA/NVCC/OptiX availability, and GEOS readiness;
- `--skip-validation` is limited to the two large timing replacement rows;
- the intake rejects missing artifacts and dirty-source markers;
- the runbook uses clean clone/build/preflight/batch/package flow;
- no public speedup wording is authorized by these files.

## Local Verification

Passed:

`PYTHONPATH=src:. python3 -m unittest tests.goal1170_clean_source_rtx_batch_manifest_test tests.goal1171_clean_source_rtx_pod_preflight_test tests.goal1172_clean_source_rtx_pod_runbook_test -q`

`git diff --check` passed for the Goal1170-Goal1172 files.

## Boundary

This consensus closes the pre-pod preparation package only. It does not run the
pod, accept future pod artifacts, or authorize public RTX speedup wording.
