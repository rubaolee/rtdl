# Claude Review: Goal3894 Clean-Provenance Scale Smoke

## Scope

Read-only review of the Goal3894 artifact (a rerun of the ten-app A5000
scale-profile smoke that records source/hardware provenance inside
`summary.json` rather than only in the markdown report). Files inspected:

- `scripts/goal3828_current_benchmark_scale_profile_runner.py`
- `docs/reports/goal3894_current_scale_with_runtime_provenance_a5000_2026-06-08.md`
- `docs/reports/goal3894_current_scale_with_runtime_provenance_a5000/summary.json`
- `docs/reports/goal3894_current_scale_with_runtime_provenance_a5000/exit_code`
- `docs/reports/goal3894_current_scale_with_runtime_provenance_a5000/outputs/*.stdout.json`
- `tests/goal3894_current_scale_with_runtime_provenance_a5000_test.py`
- Prior provenance reports/reviews for Goal3890/3891/3892/3893

I did not run the test suite or the runner (no GPU/pod access from this
environment); this is a static review of the artifact, runner code, and test.

## Q1 — Does the artifact prove a full ten-app A5000 scale smoke passed from a fresh clean clone?

Yes. `exit_code` is `0`, `summary.json` reports `"all_pass": true`,
`"json_pass_count": 10`, and `len(rows) == 10`, with each row showing
`status: "pass"` and `returncode: 0`. The report records the pod, the fresh
clone path (`/root/rtdl_goal3894_runner_1780899518`), source commit
`506bdf3c`, and GPU identity `NVIDIA RTX A5000, 580.126.09, 24564 MiB`,
matching `runtime_environment.cwd` / `source_commit_short` / `nvidia_smi`
inside `summary.json` (lines 1314-1330).

## Q2 — Does `summary.json` carry full runtime provenance, not just the report?

Yes. `summary.json["runtime_environment"]` (lines 1314-1330) contains:

- `source_commit` / `source_commit_short`: `506bdf3cd8a14ecc603df47f03d2be5e59fc1afa` / `506bdf3c`
- `working_tree_clean: true`, `git_status_short: []` (empty, as required)
- `cwd`, `python_executable`, `python_version`
- `rt_library_env` (`RTDL_OPTIX_LIBRARY`, `RTDL_OPTIX_LIB`, `RTDL_EMBREE_LIBRARY`, `RTDL_HIPRT_LIBRARY`, `CUDA_VISIBLE_DEVICES`)
- `nvidia_smi: "NVIDIA RTX A5000, 580.126.09, 24564 MiB"` — a real GPU string, not a placeholder

The runner code (`scripts/goal3828_current_benchmark_scale_profile_runner.py:131-156`,
`_runtime_environment_metadata`) computes these via `git rev-parse HEAD`,
`git status --short`, `sys.executable`, `os.environ`, and `nvidia-smi
--query-gpu=...`, and is called immediately after row selection
(`scripts/goal3828_current_benchmark_scale_profile_runner.py:285`), i.e.
before `output_dir` is created — exactly the ordering fix Goal3892
introduced (and Goal3892's own dry-run evidence demonstrated). `git log`
shows no commit touching this runner since Goal3892 (`682533e3`), confirming
Goal3894 reused the already-promoted, already-reviewed runner rather than
introducing new untested code.

One nuance worth naming explicitly (not a defect): the embedded `git_commit`
/ `git_status_short` fields *inside* the `spatial_rayjoin` row's own stdout
JSON show `"?? docs/reports/goal3894_current_scale_with_runtime_provenance_a5000/"`
— that script captures its own provenance mid-run, *after* the runner has
already created the output directory, so it legitimately observes the new
untracked path. This is a different (and later) snapshot than the top-level
`runtime_environment`, which is captured pre-output-creation per the Goal3892
fix; the two are not in tension, and the artifact is internally consistent
about *when* each snapshot was taken.

## Q3 — Do all ten row outputs parse and preserve empty claim-flag violation lists?

Yes. Each of the ten `rows[].semantic_stdout_check` blocks shows
`stdout_json_parseable: true`, `stdout_json_error: null`, and
`claim_flag_violations: []`. I confirmed this for all ten row IDs:
`hausdorff_xhd_scale_default_optix_threshold`,
`spatial_rayjoin_public_cdb_representative_mixed_route_scale_default`,
`rt_dbscan_optix_numba_scale_default_65536_no_validation`,
`robot_collision_optix_scale_default_1024_no_probe_reference`,
`contact_manifold_optix_scale_default_grid64`,
`raydb_style_optix_count_scale_default_262k`,
`barnes_hut_numba_scale_default_8192`,
`librts_spatial_index_optix_scale_default_32768`,
`rtnn_prepared_optix_scale_default_65536`, and
`triangle_counting_optix_rt_graph_2a1_scale_default_2048`. The forbidden-flag
scanner (`FORBIDDEN_TRUE_FLAGS`, lines 27-44) covers `release_authorized`
(and versioned variants), `public_speedup_claim_authorized`,
`whole_app_speedup_claim_authorized`, `broad_rt_core_claim_authorized` (and
`_speedup_` variant), `paper_reproduction_claim_authorized`,
`true_zero_copy_claim_authorized`/`true_zero_copy_authorized`,
`automatic_partner_selection_authorized`,
`app_specific_native_engine_logic_allowed`, and
`amd_performance_claim_authorized` — a superset of the boundary terms named
in the report.

## Q4 — Does the RTNN row stay on `prepared_optix_ranked_summary`?

Yes. `rows[].command` for `app: "rtnn"` (`row_id:
rtnn_prepared_optix_scale_default_65536`) invokes
`rtdl_rtnn_benchmark_app.py --mode prepared_optix_ranked_summary ...`
(lines 860-878), and the corresponding stdout artifact
(`outputs/rtnn_prepared_optix_scale_default_65536.stdout.json`) reports
`"mode": "prepared_optix_ranked_summary"`, contains a
`prepared_session_residency` block, and its `claim_boundary` carries
`automatic_partner_selection_authorized: false` and
`true_zero_copy_claim_authorized: false`. No `prepared_session_reuse_idiom`
row ID appears anywhere in `summary.json`. This matches the assertions in
`tests/goal3894_current_scale_with_runtime_provenance_a5000_test.py:47-57`.

## Q5 — Does the report avoid overclaim wording?

Yes. The only occurrences of "public speedup", "whole-app", "broad RT-core",
"paper-reproduction", "true-zero-copy", "AMD", "automatic partner", and
"app-specific … engine" in the report are inside the explicit Boundary
section's negation list ("Goal3894 does not authorize … or app-specific
native-engine logic" — lines 56-59), framed alongside "It is not a public
performance comparison and not a release packet" (line 62). No affirmative
claim language of these kinds appears in Purpose, Environment, Result, or
Interpretation.

## Test coverage

`tests/goal3894_current_scale_with_runtime_provenance_a5000_test.py` checks
exit code, `all_pass`, row count and pass status, empty
`claim_flag_violations`, the four prepared-session-profiled rows, all of the
`runtime_environment` fields named in Q2, the RTNN mode/claim-boundary
assertions from Q4, and that the report contains the required provenance and
boundary phrases. This is a faithful, artifact-grounded test of the claims
made in the report — I did not execute it, but its assertions line up
one-to-one with what I independently verified by reading `summary.json` and
the row stdout files directly.

## Verdict

**accept**

The artifact substantiates a clean, full ten-app A5000 scale-profile pass
from a fresh clone at commit `506bdf3c`, with runtime provenance (source
commit, clean Git status, Python/runtime, RTDL library env, and real A5000
GPU identity) recorded inside `summary.json` itself rather than only in
prose. The runner code is unchanged since the already-reviewed Goal3892
provenance-ordering fix, all ten rows parse with empty claim-flag violation
lists, the RTNN row stays on the promoted `prepared_optix_ranked_summary`
path, and the report's boundary section correctly frames this as an internal
smoke — not a release packet, public comparison, or any of the named
overclaim categories.
