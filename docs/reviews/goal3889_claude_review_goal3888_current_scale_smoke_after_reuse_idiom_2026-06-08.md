# Claude Review: Goal3888 Current Scale Smoke After Reuse Idiom

## Scope

Read-only external review of the Goal3888 A5000 ten-app scale-profile smoke
artifact, run after the Goal3886/3887 RTNN prepared-session reuse idiom
landed. Reviewed:

- `docs/reports/goal3888_current_scale_after_reuse_idiom_a5000_2026-06-08.md`
- `docs/reports/goal3888_current_scale_after_reuse_idiom_a5000/summary.json`
- `docs/reports/goal3888_current_scale_after_reuse_idiom_a5000/runner.log`
- `docs/reports/goal3888_current_scale_after_reuse_idiom_a5000/exit_code`
- `docs/reports/goal3888_current_scale_after_reuse_idiom_a5000/outputs/*.stdout.json`
- `tests/goal3888_current_scale_after_reuse_idiom_a5000_test.py`
- `scripts/goal3828_current_benchmark_scale_profile_runner.py`

No commands were executed against the pod; this is a static review of the
committed artifact, test, and runner source. I did not run the test suite
(no local pod/CUDA environment), but inspected the artifact directly against
each assertion the test makes.

## Findings by Review Question

**1. Clean latest-commit A5000 smoke with `all_pass=true`, `json_pass_count=10`, exit code `0`?**

Yes. `exit_code` contains `0`; `summary.json` top level has
`"all_pass": true` and `"json_pass_count": 10`; `rows` has exactly 10 entries,
all with `"status": "pass"` and `"returncode": 0`. `runner.log` shows all ten
steps (`1/10` … `10/10`) completing with `status=pass`, matching the
per-row `elapsed_sec` values reported in the markdown table. The recorded
`git_commit` inside the rayjoin row's stdout (`7c7137faf44bad598685233b8ad59b956a1d418e`)
matches the report's stated source commit `7c7137fa`.

**2. Do all parsed row payloads have empty claim-flag violations?**

Yes. All ten `semantic_stdout_check.claim_flag_violations` arrays are `[]`
(verified at lines 229, 296, 358, 417, 475, 540, 592, 821, 1060, 1268 of
`summary.json`), and `stdout_json_parseable` is `true` for each row with
non-zero `stdout_bytes`. The runner's `_find_forbidden_true_flags` walks the
full parsed JSON tree and flags any of `release_authorized`,
`public_speedup_claim_authorized`, `broad_rt_core_claim_authorized`,
`true_zero_copy_claim_authorized`, `automatic_partner_selection_authorized`,
`app_specific_native_engine_logic_allowed`, etc. set to `true` anywhere in the
payload (`scripts/goal3828_current_benchmark_scale_profile_runner.py:27-44,64-74`),
so an empty violations list is a meaningful, non-trivial pass — not just an
absence of the keys.

**3. Does the promoted RTNN row remain `prepared_optix_ranked_summary` rather than `prepared_session_reuse_idiom`?**

Yes. The `rtnn` row's command uses `--mode prepared_optix_ranked_summary`
(`summary.json:864-865`), its `row_id` is
`rtnn_prepared_optix_scale_default_65536`, and the parsed stdout payload's
top-level `"mode"` field is `"prepared_optix_ranked_summary"` (confirmed by
direct grep of the stdout JSON file). No row in the artifact has
`row_id == "prepared_session_reuse_idiom"` or any command referencing the new
idiom mode — the reuse-idiom tutorial path from Goal3886/3887 is correctly
absent from this promoted scale runner. This matches the report's claim that
"the idiom mode is not part of the scale runner."

**4. Are the four prepared-session-profiled rows correctly recorded and still non-authorizing?**

Yes. Exactly four rows carry `"prepared_session_residency_profiled": true`
(lines 224, 816, 1055, 1263): `hausdorff_xhd_scale_default_optix_threshold`,
`librts_spatial_index_optix_scale_default_32768`,
`rtnn_prepared_optix_scale_default_65536`, and
`triangle_counting_optix_rt_graph_2a1_scale_default_2048` — exactly the four
named in the report's "scene-heavy prepared rows" list and matching the
markdown table's "Prepared-session profiled" column. The top-level
`prepared_session_residency_summary` records `app_count: 4`,
`row_count: 4`, `geomean_prepare_to_hot_query_ratio: 425.19...`
(matching the report's stated geomean), and all of
`release_authorized`, `public_speedup_claim_authorized`,
`broad_rt_core_claim_authorized`, `true_zero_copy_claim_authorized`, and
`automatic_partner_selection_authorized` are `false`. Each individual
profile's nested `policy`/`timing` blocks repeat the same non-authorizing
flags consistently.

**5. Does the report avoid public speedup/release/true-zero-copy/broad RT-core/automatic-partner-selection overclaims?**

Yes. A targeted scan of the report markdown for
`speedup|release-ready|true.zero.copy|broad RT-core|paper reproduction|partner selection|automatic`
matches only the single boundary-disclaimer sentence
(`docs/reports/..._2026-06-08.md:81-83`), which explicitly *disclaims*
release action, public speedup wording, broad RT-core wording,
true-zero-copy wording, and automatic partner/backend selection — it never
asserts any of these in the affirmative. The "Interpretation" section frames
the result purely as confirmation that "the promoted ten-app scale runner
still passes" and that the idiom addition "does not replace or perturb the
benchmark path," consistent with the artifact's `internal_*_not_release_authorization`
status strings throughout `summary.json`.

## Test Alignment

`tests/goal3888_current_scale_after_reuse_idiom_a5000_test.py` checks exactly
the properties enumerated above (exit code, `all_pass`, row count, profile
count, per-row `claim_flag_violations == []`, the RTNN row's `mode` and
absence of an idiom-mode row, the geomean threshold, and required report
phrases). Every assertion in the test corresponds to a value I directly
observed in the artifact:

- `EXIT_CODE` reads `"0"` ✓
- `summary["all_pass"] is True`, `json_pass_count == 10`, `len(rows) == 10`,
  `selected_prepared_session_residency_profile_count == 4` ✓
- per-row `status == "pass"`, `stdout_json_parseable`, `claim_flag_violations == []`,
  `stdout_bytes > 0` ✓ for all ten rows
- `prepared_session_residency_summary["app_count"] == 4` and
  `geomean_prepare_to_hot_query_ratio > 400.0` (actual 425.19) ✓, all five
  authorization flags `False` ✓
- `"rtnn_prepared_optix_scale_default_65536"` present, no
  `"prepared_session_reuse_idiom"` row id, stdout `mode ==
  "prepared_optix_ranked_summary"`, `prepared_session_residency` key present,
  `automatic_partner_selection_authorized`/`true_zero_copy_claim_authorized`
  both `False` ✓
- report contains all eight required phrases (spot-checked "Goal3888",
  "NVIDIA RTX A5000", "7c7137fa", "all_pass", "json_pass_count",
  "selected prepared-session-profiled rows", "not a public performance
  comparison", "does not authorize release action") ✓

The `REPORT` path constructed by the test
(`ROOT / "docs" / "reports" / "goal3888_current_scale_after_reuse_idiom_a5000_2026-06-08.md"`)
correctly resolves to the actual report file.

## Boundary Assessment

The artifact and report consistently carry `internal_*_not_release_authorization`
/ `internal_profile_registry_not_release_authorization` status strings and
`false` authorization flags throughout, with no row tripping the runner's
forbidden-true-flag scan. The report explicitly frames itself as "a latest-commit
A5000 smoke after Goal3886," "not a fresh v2.10 release packet," and "not a
public performance comparison." This is consistent with the non-authorizing
posture established by Goal3828/3874 and carried forward correctly.

## Verdict

**accept**

The artifact genuinely demonstrates a clean ten-row A5000 scale smoke at
commit `7c7137fa` with `all_pass=true`, exit code `0`, zero claim-flag
violations across all parsed payloads, the RTNN promoted row unchanged at
`prepared_optix_ranked_summary` (with the new `prepared_session_reuse_idiom`
mode correctly absent from the promoted runner), exactly four
prepared-session-profiled rows recorded with non-authorizing flags, and a
report that stays within its stated non-authorizing, non-public-performance
boundary. The companion test's assertions all line up with the artifact's
actual contents.
