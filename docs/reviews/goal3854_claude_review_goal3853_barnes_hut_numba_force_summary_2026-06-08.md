# Goal3854: Claude Review of Goal3853 Barnes-Hut Numba Force-Summary Timing

Date: 2026-06-08

Reviewer: Claude (independent, read-only)

Verdict: **accept**

## Scope Reviewed

- `examples/v2_0/apps/simulation/rtdl_barnes_hut_force_app.py`
  (`_run_partner_exact_force_summary` / `_sum_partner_column` at lines
  498-570, the `partner_exact_force` + `output_mode == "force_summary" and
  skip_validation` branch in `run_app` at lines 600-630, the prior
  `_run_partner_exact_forces` row-materializing path at lines 469-495 and
  631-670)
- `examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py`
  (`partner_exact_force` mode dispatch at lines 1462-1479, the
  `query_repeat=query_repeat, warmup=warmup` forwarding added by Goal3853)
- `src/rtdsl/app_adapters/barnes_hut.py`
  (`pairwise_inverse_square_force_2d_partner_columns` at lines 181-355,
  including the `runtime["sync"]()` call at line 327 and the numba
  block-reduce kernel selection at lines 297-307)
- `docs/reports/goal3853_barnes_hut_numba_force_summary_2026-06-08.md`
- `docs/reports/goal3853_barnes_hut_numba_force_summary_a5000/`
  (`barnes_hut_numba_force_summary_8192.json`, `scale_profile_summary.json`,
  `outputs/barnes_hut_numba_scale_default_8192.{stdout.json,stderr.txt}`)
- `tests/goal3853_barnes_hut_numba_force_summary_test.py`

## Validation Note (process limitation)

The handoff asked for:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal3853_barnes_hut_numba_force_summary_test tests.goal3828_current_benchmark_scale_profile_registry_test
```

In this session every invocation of `py` (directly, via `cmd /c`, and via
PowerShell with `$env:PYTHONPATH` set) was blocked by the tool harness with
"This command requires approval" / "Command modifies environment variables",
and the approval prompt did not reach the user (an `AskUserQuestion` to
explicitly request approval also errored out). I was not able to execute the
suite. To compensate, I performed a close static read of the implementation
against the committed A5000 evidence artifacts, cross-checked every numeric
claim in the report against the raw JSON payloads, and read the test file's
assertions in full against the source/artifacts they check. **This review is
therefore based on static/artifact analysis, not a live test run; the user
should run the suite (or re-run this review once the harness will approve
`py`) before treating the validation gate as formally closed.**

## Findings By Question

### 1. App-agnostic native-engine boundary preserved?

Yes. `_run_partner_exact_force_summary` is pure host-side wiring: it reuses
the existing generic `rt.weighted_point_rows_to_partner_columns` and
`rt.pairwise_inverse_square_force_2d_partner_columns` adapters unchanged — no
new native symbol, kernel, or Barnes-Hut-shaped ABI is introduced anywhere in
the diff (`git show a322d895` touches only the app/benchmark/report/test/
artifact files, not `src/rtdsl`). The returned payload still carries
`native_continuation_active: false`, `native_continuation_backend: "none"`,
`rt_core_accelerated: false`, `native_engine_row_contract:
"not_called_partner_reference_only"`, and the same
`"Exact all-pairs force-vector reference path only..."` boundary string as
the pre-existing `_run_partner_exact_forces` path. The boundary is preserved.

### 2. Does the force-summary path honestly avoid Python force-row dictionaries while still producing the documented checksum?

Yes, and the framing is accurately scoped. `_run_partner_exact_force_summary`
calls `rt.pairwise_inverse_square_force_2d_partner_columns` directly on the
*reused* prepared partner columns (`prepared_partner_columns_reused: True`)
and reduces the resulting device-resident `force_x`/`force_y` columns to two
scalars via `_sum_partner_column` — for `cupy`/`torch` this sum happens
device-side (`cupy.sum(...)`, `column.detach().sum()`); for `numba` it copies
the small `(source_count,)` result vectors to host and calls `.sum()`. At no
point does it build the per-body `{"body_id": ..., "force_x": ..., "force_y":
...}` dictionaries that `_run_partner_exact_forces` /
`_partner_column_to_list` build for the `full` output mode. The
`materializes_python_force_rows: False` flag is therefore an honest claim
about *that specific* materialization (per-body Python row dicts), not a
broader "nothing touches the host" claim — and the report/metadata never
overstate it that way. `force_row_count` is reported as
`int(metadata["source_count"])`, matching `len(force_rows)` in the row-based
path, so the summary and full paths stay numerically consistent.

### 3. Is `median_force_kernel_sec ~= 0.009s` supported by the A5000 artifacts?

Yes. The direct artifact
(`barnes_hut_numba_force_summary_8192.json` →
`partner_metadata.prepared_force_repeat_protocol.median_force_kernel_sec`)
records `0.008967612870037556`, which the report rounds to `0.008967613`
(table value matches verbatim, satisfying the test's literal-substring
check). The independently-run scale-profile registry row
(`scale_profile_summary.json` → `rows[0]`, captured in
`outputs/barnes_hut_numba_scale_default_8192.stdout.json`) reports a close
but distinct `0.008946348913013935` for the same `repeat=3, warmup=1,
body_count=8192` configuration — consistent with two separate process
invocations of a ~9 ms GPU kernel, not a copy-pasted number. Both values
round to "about 9 ms," and both are well under the test's `< 0.02` assertion
bound (`test_a5000_direct_artifact_records_hot_kernel_and_no_row_summary`,
`test_a5000_runner_row_passes_and_keeps_process_boundary_visible`). The timing
also wraps a real device sync: `pairwise_inverse_square_force_2d_partner_
columns` calls `runtime["sync"]()` (line 327 of `barnes_hut.py`) before
returning, and `_run_partner_exact_force_summary` measures
`time.perf_counter()` around that whole call, so `elapsed_sec` reflects
completed kernel execution rather than asynchronous launch latency.

### 4. Does the report correctly avoid overclaiming a cold-process speedup?

Yes. The "Interpretation" section explicitly states "This goal does not
produce a large cold-process wall-clock improvement" and frames the ~9 ms
kernel against a `~1.75 s` total process elapsed — a number that matches
`scale_profile_summary.json → rows[0].elapsed_sec = 1.751682193018496`
(rounded to "about `1.75 s`" in the prose, and the table's
`runner process elapsed | 1.751682193` is verbatim). It correctly attributes
the gap to import / Numba CUDA JIT / body generation / process startup, and
explicitly redirects future effort toward "cold-start and residency: kernel
caching, persistent prepared sessions, or a larger resident benchmark
harness" rather than another micro-optimization of the already-tiny kernel.
The "Boundary" section reiterates "not an RT-core claim... not a public
speedup claim, and not release authorization." No wording in the report,
metadata, or artifacts authorizes a whole-app or cold-process speedup claim
(`whole_app_speedup_claim_authorized`, `public_speedup_claim_authorized`,
`release_authorized` are all `false` throughout).

### 5. Does forwarding `query_repeat`/`warmup` into `partner_exact_force` preserve prior behavior for non-summary / validation-inclusive modes?

Yes. `run_benchmark`'s `partner_exact_force` branch now always forwards
`query_repeat=query_repeat, warmup=warmup` into `app.run_app`, but inside
`run_app` those values are only *consumed* by the new
`output_mode == "force_summary" and skip_validation` branch. Every other
combination — `output_mode="full"`, or `force_summary` with
`skip_validation=False` — still falls through to
`_run_partner_exact_forces(bodies, partner=partner)`, whose signature does
not accept `query_repeat`/`warmup` at all; the values are silently accepted
and ignored, exactly as they were (silently dropped at the wrapper level)
before Goal3853. `run_app`'s top-level validation
(`query_repeat <= 0` / `warmup < 0` → `ValueError`, lines 593-596) is
unchanged and applies uniformly regardless of backend, so no new validation
behavior leaks into the non-summary paths either. The scoping is also
substantively correct, not just incidentally safe: the validation-inclusive
paths need full per-body force rows to compute `error_rows` /
`max_relative_error` against the brute-force oracle, so they cannot skip row
materialization — the repeat/warmup optimization is only meaningful (and only
applied) where `skip_validation=True` removes that requirement.

### 6. Required-before-next-step fixes?

None found. The change is a narrow, additive host-side timing/accounting fix
that:
- reuses existing generic partner adapters without adding native surface,
- correctly separates JIT/launch overhead from steady-state kernel cost via
  `warmup`/`repeat` and a measured median,
- produces a checksum (`checksum_force_x ≈ -1.31e-10`,
  `checksum_force_y ≈ 9.31e-10`) that is consistent with a physically
  sensible near-zero net force for this symmetric body fixture, and
- is honestly bounded in both the report and the runtime metadata
  (`whole_app_speedup_claim_authorized`, `rt_core_speedup_claim_authorized`,
  `v2_0_release_authorized` all `false`).

The only open item is procedural, not a code defect: the validation command
could not be executed in this session (see "Validation Note"), so the user
should run it directly to formally close that gate.

## Test File Assessment

`tests/goal3853_barnes_hut_numba_force_summary_test.py` checks: the new
helper names/flags/contract strings appear in the app source
(`_run_partner_exact_force_summary`, `prepared_partner_columns_reused`,
`materializes_python_force_rows`, `force_summary_materialization_sec`,
`prepared_force_repeat_protocol`,
`rt.pairwise_inverse_square_force_2d_partner_columns`); the benchmark wrapper
forwards `query_repeat=query_repeat` / `warmup=warmup` into the
`partner_exact_force` dispatch; the report contains the literal
`0.008967613`, `materializes Python force rows | \`false\``, and the
`cold-process` / `kernel caching` / `not a public speedup claim` / `not
release authorization` boundary phrases; the direct A5000 artifact has
`body_count=8192`, `partner="numba"`, `output_mode="force_summary"`,
`materializes_python_force_rows=False`, `prepared_partner_columns_reused=True`,
`repeat=3`/`warmup=1`, `median_force_kernel_sec < 0.02`,
`force_summary_materialization_sec < 0.01`, and both speedup-claim flags
`False`; and the runner summary row passes with `status="pass"`,
`stderr_bytes=0`, no claim-flag violations, `elapsed_sec > 1.0`, and the
file-backed payload's `median_force_kernel_sec < 0.02`. I checked every one of
these assertions against the committed source and JSON artifacts — they all
match exactly as written, so the suite should pass once it can be run.

## Overall Verdict

**accept.** Goal3853 is a small, honest, additive accounting fix: it makes
`--repeat`/`--warmup` actually reach the `partner_exact_force` summary path
(where they were previously silently dropped), reduces the force-summary mode
to a device-resident checksum without constructing per-body Python row dicts,
and reports a measured, synced, steady-state kernel median (~9 ms) that is
fully consistent with both committed A5000 artifacts. The report correctly
frames this as an app-level Numba accounting improvement — not a cold-process,
RT-core, or public speedup claim — and explicitly redirects future effort
toward cold-start/residency rather than further micro-optimizing an
already-negligible kernel. No native-engine boundary issues, no
overclaiming, and no behavioral regression in the non-summary /
validation-inclusive `partner_exact_force` paths. The one caveat is that the
required validation command could not be executed in this session due to a
tooling/permission block — the user should run it (or have it re-run) to
close that gate formally; the static evidence strongly suggests it will pass
as written.
