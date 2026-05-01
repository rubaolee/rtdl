# Goal1173 External Review Request

Please review the staged source archive manifest tool.

Files:

- `scripts/goal1173_staged_source_archive_manifest.py`
- `tests/goal1173_staged_source_archive_manifest_test.py`
- `docs/reports/goal1173_staged_source_archive_manifest_2026-04-30.json`
- `docs/reports/goal1173_staged_source_archive_manifest_2026-04-30.md`
- `docs/reports/goal1169_clean_source_rtx_claim_grade_batch_plan_2026-04-30.md`

Local validation:

- `PYTHONPATH=src:. python3 scripts/goal1173_staged_source_archive_manifest.py`
- `PYTHONPATH=src:. python3 -m unittest tests.goal1173_staged_source_archive_manifest_test -q`
- `git diff --check` on the Goal1173 files

Question:

Is Goal1173 a technically safe preparatory step for the alternate "staged source
archive with exact manifest" source mode allowed by Goal1169?

Check:

- the tool creates a deterministic file list and aggregate digest over source-relevant roots;
- build artifacts and binary outputs are excluded;
- the manifest is only preparatory and does not itself authorize claim-grade pod artifacts or public wording;
- the tests cover source-root inclusion and build-output exclusion;
- any future use of this path would still need an actual archive, digest, pod run, copied artifacts, intake, and external review.

Write verdict to:

`docs/reports/goal1173_external_review_2026-04-30.md`

Use `VERDICT: ACCEPT` only if correct and conservative. Use `VERDICT: BLOCK`
with exact required fixes otherwise.
