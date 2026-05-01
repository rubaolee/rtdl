# Goal1175 External Review Request

Please review the staged source archive builder and generated archive metadata.

Files:

- `scripts/goal1175_staged_source_archive_builder.py`
- `tests/goal1175_staged_source_archive_builder_test.py`
- `docs/reports/goal1175_staged_source_archive_2026-04-30.json`
- `docs/reports/goal1175_staged_source_archive_2026-04-30.md`
- `docs/reports/goal1175_staged_source_archive_verify_2026-04-30.json`
- `docs/reports/goal1175_rtdl_staged_source_2026-04-30.tar.gz`
- `docs/reports/goal1173_two_ai_consensus_2026-04-30.md`
- `docs/reports/goal1174_two_ai_consensus_2026-04-30.md`

Local validation:

- `PYTHONPATH=src:. python3 scripts/goal1175_staged_source_archive_builder.py`
- `PYTHONPATH=src:. python3 -m unittest tests.goal1175_staged_source_archive_builder_test -q`
- `PYTHONPATH=src:. python3 scripts/goal1175_staged_source_archive_builder.py --archive docs/reports/goal1175_rtdl_staged_source_2026-04-30.tar.gz --output-json docs/reports/goal1175_staged_source_archive_verify_2026-04-30.json --verify-sha256 <archive_sha256>`

Question:

Is Goal1175 technically safe as an actual staged-source archive path for the
next pod run, assuming the archive SHA256 and manifest reports are preserved?

Check:

- the archive is built from the Goal1173 manifest source set;
- the archive records SHA256, byte size, file count, and manifest aggregate digest;
- the verification JSON proves the current archive matches the recorded SHA256;
- the archive is still only source material, not benchmark evidence;
- using this archive on a pod still requires extraction, preflight, batch run, copyback, intake, and external review before any public wording.

Write verdict to:

`docs/reports/goal1175_external_review_2026-04-30.md`

Use `VERDICT: ACCEPT` only if correct and conservative. Use `VERDICT: BLOCK`
with exact required fixes otherwise.
