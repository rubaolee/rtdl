# Goal682 v0.9.6 Release-Candidate Package Review Request

Please review Goal682 and return `ACCEPT` or `BLOCK`.

Primary report:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal682_v0_9_6_release_candidate_package_2026-04-21.md`

Release-candidate package:

- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_6/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_6/release_statement.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_6/support_matrix.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_6/audit_report.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_6/tag_preparation.md`

Public docs touched:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/current_main_support_matrix.md`

Verification:

- `PYTHONPATH=src:. python3 -m unittest tests.goal682_v0_9_6_release_candidate_package_test tests.goal645_v0_9_5_release_package_test tests.goal646_public_front_page_doc_consistency_test tests.goal654_current_main_support_matrix_test tests.goal655_tutorial_example_current_main_consistency_test -v`
  - result: `17` tests OK
- `PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py --write`
  - result: valid, `250` commands across `14` docs
- `PYTHONPATH=src:. python3 scripts/goal497_public_entry_smoke_check.py`
  - result: valid
- `git diff --check`
  - result: clean

Boundary to verify:

- The current released version remains `v0.9.5`.
- `v0.9.6` is a release candidate only and is not tagged.
- Tag/push commands are present only as held commands and must not be run
  without explicit maintainer authorization.
- No broad DB, graph, full-row, one-shot, GTX 1070 RT-core, AMD GPU, or Apple
  RT full-row speedup claim is made.
