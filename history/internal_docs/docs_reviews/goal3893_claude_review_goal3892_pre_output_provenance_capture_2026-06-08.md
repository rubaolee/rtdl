# Claude Review: Goal3892 Pre-Output Provenance Capture

Date: 2026-06-08

Reviewer: Claude (independent read-only review)

Verdict: **accept**

## Summary

Goal3892 fixes an ordering bug that Goal3890's own A5000 dry run exposed: the
runner called `_runtime_environment_metadata()` *after* `output_dir.mkdir(...)`,
so the freshly-created (untracked) output directory showed up in
`git_status_short` and forced `working_tree_clean` to `false` even on an
otherwise-clean checkout. Goal3892 moves the call to immediately after row
selection — before `output_dir` is computed or created and before any JSON is
written — and stores the result in a local (`runtime_environment`) that is
threaded into `result["runtime_environment"]` unchanged.

I read the runner diff (`git diff 8618467b 682533e3 --
scripts/goal3828_current_benchmark_scale_profile_runner.py`), the full `main()`
body (`runner.py:259-379`), the unchanged `_run_metadata_command` /
`_runtime_environment_metadata` helpers (`runner.py:112-156`), the new
regression test, the report, and both new/changed artifact files
(`docs/reports/goal3892_pre_output_provenance_a5000_dry_run/{summary.json,exit_code,stdout.json,stderr.txt}`).
I could not execute `pytest`/`unittest` in this environment — see "Note on test
execution" below — so this remains a static/artifact review, not a
test-execution confirmation.

## Findings (ordered by severity)

No correctness or honesty issues found. Notes below are confirmations.

1. **(Info) The fix is exactly the ordering change the report claims, and
   nothing else.** `git diff 8618467b 682533e3` shows a 2-line change: one
   insertion (`runtime_environment = _runtime_environment_metadata()` at
   `runner.py:285`, immediately after the `if not rows: raise SystemExit(...)`
   guard and *before* `output_dir = args.output_dir` at `runner.py:286`) and
   one substitution (`"runtime_environment": _runtime_environment_metadata()`
   → `"runtime_environment": runtime_environment` at `runner.py:301`, now
   reusing the pre-computed value instead of calling the function a second
   time at dict-construction time, which also avoids capturing two slightly
   different snapshots). `output_dir.mkdir(parents=True, exist_ok=True)`
   (`runner.py:292`) and the `output_json.write_text(...)` call
   (`runner.py:372-373`) both still execute strictly after the capture.
   `_run_metadata_command` and `_runtime_environment_metadata`
   (`runner.py:112-156`) are byte-for-byte unchanged from Goal3890 — same
   bounded `subprocess.run` with `timeout=10`, `check=False`, and
   `(OSError, subprocess.TimeoutExpired)` caught to `None`, same five
   `rt_library_env` keys, same `git status --short` / `git rev-parse HEAD` /
   `nvidia-smi` probes. **Answers Q1 and Q4**: yes, capture now happens before
   any output directory/file is created, and row execution, stdout parsing,
   prepared-session attachment (`_attach_prepared_session_profile`,
   `runner.py:331-334` / `357-362`), and the claim scanner
   (`FORBIDDEN_TRUE_FLAGS`, `_find_forbidden_true_flags`, `runner.py:216-217`)
   are untouched.

2. **(Info) The new regression test exercises exactly the failure mode the fix
   addresses, and would have failed against the pre-fix code.**
   `test_runtime_environment_is_captured_before_output_directory_creation`
   (`tests/goal3890_scale_runner_runtime_provenance_test.py:64-95`) runs the
   runner with `--dry-run --only rtnn --output-json
   docs/reports/_goal3892_pre_output_provenance_test/summary.json`. With
   `--output-json` set and no `--output-dir`, the runner derives `output_dir =
   args.output_json.parent / "outputs"` (`runner.py:289`), so `mkdir` creates
   the brand-new, untracked `docs/reports/_goal3892_pre_output_provenance_test/`
   tree. Under the pre-fix ordering (metadata captured *after* `mkdir`), `git
   status --short` would have reported `??
   docs/reports/_goal3892_pre_output_provenance_test/` and the test's
   `assertNotIn(...)` would fail — this is precisely the bug the Goal3890 A5000
   dry run exposed (an untracked output path polluting `git_status_short`).
   Under the fixed ordering the directory does not exist yet when `git status`
   runs, so the assertion passes. The test cleans up both before (defensive,
   in case a prior failed run left the directory) and in a `finally` block
   (`shutil.rmtree`), so it leaves no residue and is safe to re-run.
   `--only rtnn` is well-chosen: I confirmed exactly one registry row has
   `app="rtnn"` (`src/rtdsl/current_benchmark_scale_profiles.py:313`), matching
   the `len(payload["rows"]) == 1` assertion and keeping the dry run minimal.
   **Answers Q2**: yes, the test correctly prevents — and would have caught —
   the runner-created output path polluting `git_status_short`.

3. **(Info) The A5000 clean-tree dry-run artifact matches every claim in the
   report and the new artifact-specific test.** I read
   `docs/reports/goal3892_pre_output_provenance_a5000_dry_run/summary.json`
   directly: `exit_code` is `"0"`, `dry_run` is `true`, `len(rows) == 1`
   (the `rtnn` row), `runtime_environment.source_commit` is
   `682533e349f44237efad9ad6d174f255f87bf922` /
   `source_commit_short` is `682533e3` (which `git log --oneline` confirms is
   exactly the "Goal3892 capture scale provenance before output" commit — the
   pod ran the freshly-pushed fix against itself), `working_tree_clean` is
   `true`, `git_status_short` is `[]`, and `nvidia_smi` is `"NVIDIA RTX A5000,
   580.126.09, 24564 MiB"` (real pod GPU info, not a placeholder). `cwd` is
   `/root/rtdl_goal3892_runner_clean_1780899172`, a fresh-clone pod path
   distinct from the dirty Goal3890 run's `cwd`
   (`/root/rtdl_goal3876_runner_1780895523`), consistent with the report's
   claim that this run was made "from a fresh clone ... without pre-creating
   the in-repo output directory." The companion `outputs/` directory the
   runner created during this run is present and empty (as expected for a dry
   run with no per-row file writes), and `stdout.json` matches `summary.json`
   byte-for-byte except for the trailing newline `print(json.dumps(...))`
   adds — i.e., the captured stdout and the written JSON file are the same
   payload, as `runner.py:373-374` would produce. Every field the new test
   `test_goal3892_a5000_artifact_records_clean_tree_when_runner_creates_output_path`
   (`tests/...:142-154`) checks is present and correct. **Answers Q3**: yes,
   on all four points (`working_tree_clean = true`, `git_status_short = []`,
   `source_commit_short = 682533e3`, real A5000 metadata).

4. **(Info) The report and its regression-test phrase-check are mutually
   consistent and accurately framed.** The report
   (`docs/reports/goal3892_scale_runner_pre_output_provenance_capture_2026-06-08.md`)
   states the change precisely ("call `_runtime_environment_metadata()`
   immediately after row selection; create `output_dir` after provenance is
   captured; store the pre-output metadata in
   `result["runtime_environment"]"`) and that matches the diff exactly — there
   is no embellishment beyond what the two-line change does. It frames the
   change as "provenance ordering only," explicitly disclaiming release
   action, public-speedup, broad-RT-core, true-zero-copy, automatic
   partner/backend selection, AMD-performance, paper-reproduction, and
   app-specific-native-engine-logic wording (lines 26-29). I grepped the
   report for all seven phrases
   `test_goal3892_report_documents_pre_output_capture`
   (`tests/...:114-125`) checks — `"Goal3892"`, `"creating output
   directories"`, `"A5000 Clean-Tree Dry-Run Evidence"`, `"682533e3"`,
   `"working_tree_clean"`, `"git_status_short"`, `"does not authorize release
   action"` — and all seven are present verbatim (lines 1, 11, 38, 52,
   53/121, 54/122, 26-27). The hardcoded `release_authorized` /
   `public_speedup_claim_authorized` / `broad_rt_core_claim_authorized` /
   `paper_reproduction_claim_authorized` flags (`runner.py:309-312`, all
   `False`) and `FORBIDDEN_TRUE_FLAGS` (`runner.py:27-44`, unchanged) remain
   the structural backstop. **Answers Q5**: I found no
   release/public-speedup/true-zero-copy/broad-RT-core/automatic-partner-
   selection overclaims in the report.

## Boundary (if accepted)

This is an internal, additive provenance-ordering fix to the current
benchmark scale-profile runner. It is **not**: release authorization, a
public speedup claim, paper reproduction, a broad RT-core claim, true-zero-copy
wording, AMD performance wording, automatic partner/backend selection, or
app-specific native-engine logic. The change only moves *when* the existing
`runtime_environment` snapshot is taken (before output-directory/file
creation rather than after) so that a runner-created output path cannot
spuriously mark `working_tree_clean = false` or pollute `git_status_short`. It
does not add, remove, or reorder any benchmark row command, change how stdout
is parsed or validated, or change how the claim-boundary scanner gates
`pass`/`fail`.

## Note on test execution

I was not able to run
`python -m pytest tests/goal3890_scale_runner_runtime_provenance_test.py` (or
`unittest`) in this review environment — `python`/`py` invocations were
declined by the harness before reaching the interpreter, consistent with the
prior Goal3891 review of this same test file. The verdict above is based on
(a) reading the two-line runner diff against the unchanged helper functions and
the surrounding `main()` control flow line-by-line, (b) reasoning through what
the new regression test would have observed under both the pre-fix and
post-fix orderings (it would have failed pre-fix and passes post-fix by
construction), (c) directly inspecting `summary.json`/`exit_code`/`stdout.json`
against every artifact-specific assertion, and (d) grepping the report for
every phrase the report-boundary test checks. I'm confident the suite passes
given this static correspondence, but a maintainer should still run it once
(or trust the pod CI run) for a live confirmation.
