# Claude Review: Goal3890 Scale Runner Runtime Provenance

Date: 2026-06-08

Reviewer: Claude (independent read-only review)

Verdict: **accept**

## Summary

Goal3890 adds a `runtime_environment` metadata block to
`scripts/goal3828_current_benchmark_scale_profile_runner.py` so that future
scale-profile artifacts self-document their source commit, working-tree
status, Python runtime, RTDL backend-library environment variables, and (when
available) `nvidia-smi` GPU info — closing the gap Goal3888 noted (the prior
report had to record commit/GPU by hand). I independently read the runner
diff (`git show 8618467b -- scripts/goal3828_current_benchmark_scale_profile_runner.py`),
the new test, the report, and the A5000 dry-run artifact
(`summary.json` + `exit_code`), and cross-checked the related runner tests
(`tests/goal3828_current_benchmark_scale_profile_registry_test.py`,
`tests/goal3876_scale_runner_prepared_session_profile_integration_test.py`)
for any assumptions the new top-level key could break.

I could not execute `pytest`/`unittest` in this environment (the harness
declined to run `python`/`py` invocations), so I did not independently confirm
the suite passes. I instead verified, by direct text/structure inspection,
that every assertion in `tests/goal3890_scale_runner_runtime_provenance_test.py`
matches what the code and artifacts actually contain (see Finding 4). This is
a read-only static/artifact review, not a test-execution confirmation.

## Findings (ordered by severity)

No correctness or honesty issues found. Notes below are confirmations.

1. **(Info) The change is additive and provenance-only — it does not touch row
   execution.** The diff (`runner.py:112-156`, `runner.py:300`) adds two new
   functions (`_run_metadata_command`, `_runtime_environment_metadata`) and a
   single new key, `"runtime_environment": _runtime_environment_metadata()`,
   inserted into the top-level `result` dict between `"summary"` and
   `"prepared_session_residency_validation"`. Nothing in `_row_command`,
   `_run_row`, `_semantic_file_check`, `FORBIDDEN_TRUE_FLAGS`,
   `_find_forbidden_true_flags`, or the dry-run/non-dry-run row-building paths
   was touched — `git show 8618467b` shows only insertions (48 lines added, 0
   removed) confined to the metadata helpers and the one new dict entry. The
   claim-boundary scanner that fails a row on forbidden-flag violations or
   unparseable stdout (`runner.py:216-217`) is untouched and remains
   fail-closed.

2. **(Info) Adding a new top-level key cannot break the sibling runner tests.**
   I grepped both related test files for `payload[`/`result[` indexing and
   found neither asserts an exact key set or count on the top-level result —
   they index specific known keys (`dry_run`, `summary`, `validation`,
   `release_authorized`, `selected_prepared_session_residency_profile_count`,
   `rows[i][...]`, etc.). `tests/goal3828_current_benchmark_scale_profile_registry_test.py:90-133`
   and `tests/goal3876_scale_runner_prepared_session_profile_integration_test.py:41-109`
   would both still pass against a payload with one extra key. The new
   `runtime_environment` field is purely additive at the JSON level.

3. **(Info) Metadata collection is bounded, side-effect-free, and fails safe.**
   `_run_metadata_command` (`runner.py:112-128`) calls `subprocess.run` with an
   argument list (no `shell=True`, so no shell-injection surface), a hard
   `timeout=10`, `check=False`, and catches `(OSError, subprocess.TimeoutExpired)`
   to return `None` rather than raising. `_runtime_environment_metadata`
   (`runner.py:131-156`) calls it exactly twice (`git status --short`,
   `git rev-parse HEAD`) plus once for `nvidia-smi`, and reads five
   `os.environ.get(...)` values that cannot raise. None of this can fail the
   benchmark run or hang it indefinitely — worst case is ~30s of bounded
   subprocess timeouts before falling back to `None`/empty values. This matches
   the report's claim (lines 33-35) that the helper is "best-effort and bounded
   by a 10-second timeout" and that missing tools yield `null` rather than
   failure.

4. **(Info) Every assertion in `tests/goal3890_scale_runner_runtime_provenance_test.py`
   matches the code and artifacts as written.** Walking the three test methods
   against the source:
   - `test_dry_run_emits_runtime_environment_provenance` checks for the keys
     `source_commit`, `source_commit_short`, `git_status_short`,
     `working_tree_clean`, `python_executable`, `python_version`, `cwd`,
     `rt_library_env` (with the exact five-key set
     `{RTDL_OPTIX_LIBRARY, RTDL_OPTIX_LIB, RTDL_EMBREE_LIBRARY,
     RTDL_HIPRT_LIBRARY, CUDA_VISIBLE_DEVICES}`), and `nvidia_smi`, plus
     `source_commit_short == source_commit[:8]` and `git_status_short` being a
     list. `_runtime_environment_metadata` (`runner.py:134-156`) returns
     exactly this shape — note `git_status_short` is built as a `tuple`
     (`runner.py:137`) but `json.dumps`/`json.loads` round-trips it to a
     `list`, satisfying `assertIsInstance(..., list)`. The four
     release/claim-authorization assertions
     (`release_authorized`/`public_speedup_claim_authorized`/
     `broad_rt_core_claim_authorized`/`paper_reproduction_claim_authorized`
     all `False`) match the hardcoded `False` literals at `runner.py:308-311`.
   - `test_report_documents_provenance_only_boundary` checks eleven phrases
     against the report text. I independently grepped the report for each: all
     eleven are present verbatim, including the `"provenance only"` /
     `"does not change any benchmark row command"` /
     `"does not authorize release action"` framing (report lines 39, 43) and
     the `"8618467b"` / `"working_tree_clean"` evidence strings (report lines
     69, 72).
   - `test_a5000_dry_run_artifact_records_runtime_environment` checks
     `exit_code == "0"`, `dry_run == true`, `len(rows) == 1`,
     `source_commit_short == "8618467b"`, `"NVIDIA RTX A5000" in nvidia_smi`,
     `cwd == "/root/rtdl_goal3876_runner_1780895523"`,
     `working_tree_clean == false`, and that `git_status_short` contains the
     `"?? docs/reports/goal3890_scale_runner_runtime_provenance_a5000_dry_run/"`
     line. I read `summary.json` and `exit_code` directly and every one of
     these values is present and matches exactly (`summary.json:244-262`,
     `exit_code:1`).

5. **(Info) The A5000 dry-run artifact demonstrates the provenance fields work
   on real pod hardware, not just in a synthetic dry run.** `summary.json`'s
   `runtime_environment` block carries pod-specific, plausible values that a
   local dry run could not fabricate: a real GPU string
   (`"NVIDIA RTX A5000, 580.126.09, 24564 MiB"`), a pod-style `cwd`
   (`/root/rtdl_goal3876_runner_1780895523`, consistent with the
   Goal3876-lineage pod working-directory naming convention used in prior
   handoffs), populated `RTDL_OPTIX_LIB`/`RTDL_OPTIX_LIBRARY`/
   `RTDL_EMBREE_LIBRARY` paths pointing at a pod build directory
   (`/root/rtdl_goal3788_clean_1780857956/build/...`), and a `source_commit`
   (`8618467b32b05df9dc360a1d910e0eba70a435b9`) that I confirmed via
   `git log --oneline` is exactly the "Goal3890 add scale runner runtime
   provenance" commit — i.e., the pod ran the freshly-pushed runner change
   against itself. `exit_code` is `0` and `dry_run` is `true`, so this is a
   clean, side-effect-free probe.

6. **(Info) The `working_tree_clean = false` caveat is honestly and
   specifically documented, not hand-waved.** Report lines 74-79 state plainly
   that the dirty value is *expected* "because the artifact was written under
   `docs/reports/goal3890_scale_runner_runtime_provenance_a5000_dry_run` before
   metadata collection," and that callers needing a clean-tree proof should use
   an external output directory or inspect `git_status_short` for the
   provenance of the dirtiness. This is exactly what the artifact shows:
   `git_status_short` contains a single line,
   `"?? docs/reports/goal3890_scale_runner_runtime_provenance_a5000_dry_run/"`
   — i.e., the *only* untracked path is the artifact directory the run itself
   was about to populate, not unrelated uncommitted work. The explanation is
   falsifiable and matches the data; it is not a vague "ignore this" caveat.

7. **(Info) No public-speedup/release/true-zero-copy/broad-RT-core/automatic-
   partner-selection overclaims.** The report frames the change strictly as
   "provenance only" (line 39) and explicitly disclaims release action, public
   speedup wording, broad RT-core wording, true-zero-copy wording, automatic
   partner/backend selection, AMD performance wording, and app-specific
   native-engine logic (lines 43-45). The runner's hardcoded top-level flags
   (`release_authorized`, `public_speedup_claim_authorized`,
   `broad_rt_core_claim_authorized`, `paper_reproduction_claim_authorized`, all
   `runner.py:308-311`) and the `claim_boundary` string
   (`CURRENT_BENCHMARK_SCALE_PROFILE_CLAIM_BOUNDARY`, unchanged) remain `False`
   / non-authorizing in both the dry-run artifact and (structurally) in any
   future non-dry-run artifact. `FORBIDDEN_TRUE_FLAGS` (`runner.py:27-44`),
   which already covered all of these wording categories plus
   `automatic_partner_selection_authorized` and
   `app_specific_native_engine_logic_allowed`, is unchanged by this commit.

## Boundary (if accepted)

This is an internal, additive provenance enhancement to the current
benchmark scale-profile runner. It is **not**: release authorization, a public
speedup claim, paper reproduction, a broad RT-core claim, true-zero-copy
wording, AMD performance wording, automatic partner/backend selection, or
app-specific native-engine logic. The new `runtime_environment` block records
*context* about how an artifact was produced (commit, tree cleanliness,
Python/library env, optional GPU string) — it does not itself constitute a
benchmark measurement, and it does not change which commands run, how their
output is validated, or how the claim-boundary scanner gates `pass`/`fail`.

## Note on test execution

I was not able to run
`python -m pytest tests/goal3890_scale_runner_runtime_provenance_test.py` (or
`unittest`) in this review environment — `python`/`py` invocations were
declined by the harness before reaching the interpreter. The verdict above is
based on (a) reading the runner diff line-by-line against the test's
assertions, (b) directly inspecting `summary.json`/`exit_code` against the
artifact-specific assertions, and (c) grepping the report for every phrase the
report-boundary test checks. I'm confident the suite passes given this static
correspondence, but a maintainer should still run it once (or trust the pod CI
run) for a live confirmation.
