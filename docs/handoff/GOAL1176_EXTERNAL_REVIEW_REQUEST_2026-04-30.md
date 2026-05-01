# Goal1176 External Review Request

Please review the pod-side staged-archive batch executor.

Files:

- `scripts/goal1176_pod_archive_batch_executor.sh`
- `tests/goal1176_pod_archive_batch_executor_test.py`
- `docs/reports/goal1176_pod_archive_batch_executor_2026-04-30.md`
- `docs/reports/goal1175_two_ai_consensus_2026-04-30.md`
- `docs/reports/goal1170_goal1171_goal1172_two_ai_consensus_2026-04-30.md`

Local validation:

- `chmod +x scripts/goal1176_pod_archive_batch_executor.sh`
- `PYTHONPATH=src:. python3 -m unittest tests.goal1176_pod_archive_batch_executor_test -q`
- `git diff --check` on Goal1176 files

Question:

Is Goal1176 safe and appropriate as the pod-side executor for the reviewed
Goal1175 staged-source archive?

Check:

- it verifies archive SHA256 before extraction;
- it extracts to a dedicated work directory;
- it installs GEOS and CUDA/OptiX build prerequisites;
- it builds OptiX before running the batch;
- it runs Goal1170 batch through the existing runner, so Goal1171 preflight still executes;
- it packages results for copyback;
- it does not authorize public speedup wording by itself.

Write verdict to:

`docs/reports/goal1176_external_review_2026-04-30.md`

Use `VERDICT: ACCEPT` only if correct and conservative. Use `VERDICT: BLOCK`
with exact required fixes otherwise.
