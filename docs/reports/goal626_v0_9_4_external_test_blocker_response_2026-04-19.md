# Goal 626: v0.9.4 External Test Blocker Response

Date: 2026-04-19

Repository: `/Users/rl2025/rtdl_python_only`

External tester report:

`/Users/rl2025/rtdl_python_only/docs/reports/external_v0_9_4_release_level_test_report_2026-04-19.md`

Response status: `ACCEPTED AFTER FIX`

## External Verdict

The external tester returned `BLOCK` against the `v0.9.4` release-level test.

The report listed three blocker classes:

1. stale release assertion in `tests/goal532_v0_8_release_authorization_test.py`
2. C++ compilation errors in compare/smoke tests
3. external baseline failure in `tests/goal207_knn_rows_external_baselines_test.py`

## Reproduction Results

### Blocker 1: stale release assertion

Status: `REPRODUCED`

Reproduction command:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal532_v0_8_release_authorization_test -v
```

Observed before fix:

- `test_public_docs_identify_v091_as_current_release_and_v08_as_released_layer`
  failed because the test still expected `v0.9.1` while public docs correctly
  said `v0.9.4`.

Fix:

- updated `tests/goal532_v0_8_release_authorization_test.py` to assert
  `v0.9.4` as the current released version.
- refreshed public-facing stale `v0.9.4 target` wording to released `v0.9.4`
  wording across README/docs/tutorial/example guidance.
- updated `tests/goal511_feature_guide_v08_refresh_test.py` to assert released
  v0.9.4 wording instead of old target wording.

### Blocker 2: C++ compilation errors in compare/smoke tests

Status: `NOT REPRODUCED LOCALLY AFTER INVESTIGATION`

Reproduction command:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal15_compare_test tests.goal17_prepared_runtime_test tests.goal19_compare_test tests.report_smoke_test -v
```

Observed locally:

- `13 tests`
- `OK`

Follow-up combined command:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal15_compare_test tests.goal17_prepared_runtime_test tests.goal19_compare_test tests.report_smoke_test tests.goal207_knn_rows_external_baselines_test -v
```

Observed locally:

- `20 tests`
- `OK`

Interpretation:

The report is still valuable because it indicates an external macOS checkout can
hit missing dependency-path behavior. On this maintained macOS environment, the
same tests use the available build configuration and pass. No code change was
made for this class in this response because the exact failure did not reproduce
and the full release-pattern suite passes.

### Blocker 3: external baseline failure

Status: `NOT REPRODUCED LOCALLY`

Reproduction command:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal207_knn_rows_external_baselines_test -v
```

Observed locally:

- `7 tests`
- `OK`

The same test also passed inside the combined focused blocker response suite and
the full release-pattern suite.

## Public Documentation Refresh

The following public-facing files were refreshed from `target` wording to
released `v0.9.4` wording where appropriate:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/current_architecture.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md`
- `/Users/rl2025/rtdl_python_only/docs/quick_tutorial.md`
- `/Users/rl2025/rtdl_python_only/docs/capability_boundaries.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/backend_maturity.md`

Stale-pattern scan:

```bash
rg -n 'Release Target Package|current `v0\.9\.4` target|v0\.9\.4 target|current v0\.9 line is released as `v0\.9\.1`|current released state is `v0\.9\.1`|current released version: `v0\.9\.1`|current released version is `v0\.9\.1`|next public Apple RT release|exact released claims wait' README.md docs/README.md docs/current_architecture.md docs/rtdl_feature_guide.md docs/quick_tutorial.md docs/capability_boundaries.md docs/tutorials/README.md docs/release_facing_examples.md docs/backend_maturity.md tests/goal532_v0_8_release_authorization_test.py
```

Result:

- no matches

## Verification After Fix

Focused public doc and release tests:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal511_feature_guide_v08_refresh_test tests.goal532_v0_8_release_authorization_test tests.goal512_public_doc_smoke_audit_test tests.goal531_v0_8_release_candidate_public_links_test tests.goal515_public_command_truth_audit_test -v
```

Result:

- `13 tests`
- `OK`

Focused blocker-response tests:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal15_compare_test tests.goal17_prepared_runtime_test tests.goal19_compare_test tests.report_smoke_test tests.goal207_knn_rows_external_baselines_test -v
```

Result:

- `20 tests`
- `OK`

Public command truth audit:

```bash
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
```

Result:

- `valid: true`
- public docs checked: `14`
- public commands checked: `244`

Full release-pattern suite:

```bash
PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py' -v
```

Transcript:

`/Users/rl2025/rtdl_python_only/docs/reports/goal626_v0_9_4_external_blocker_response_full_unittest_2026-04-19.txt`

Result:

- `1178 tests`
- `171 skips`
- `OK`
- runtime: `107.741s`

## Codex Verdict

The external `BLOCK` report was valid because it found a real stale release
assertion and public wording drift after the release tag.

After the fixes above, the reproduced blocker is resolved, the reported
C++/external-baseline failures do not reproduce on the maintained macOS
checkout, and the full release-pattern suite passes.

Codex verdict: `ACCEPT` for updating the `v0.9.4` release record to this
corrected state, pending external AI review of this response.
