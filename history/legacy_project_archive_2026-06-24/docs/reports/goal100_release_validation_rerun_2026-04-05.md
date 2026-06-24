# Goal 100 Report: Release Validation Rerun

Date: 2026-04-05
Status: accepted

## Objective

Rerun the pre-release validation gate after the Goal 98 OptiX regression repair
and Goal 99 OptiX prepared run-1 win.

Validated head:

- `e15ee77`

Fresh Linux clone used for the hard gate:

- `/home/lestat/work/rtdl_goal100_clean`

## What was rerun directly

### Local preflight

Syntax/compile sanity:

- `python3 -m py_compile ...`
- result:
  - `pass`

Focused local release slice:

- `PYTHONPATH=src:. python3 -m unittest ...`
- result:
  - `60 tests`
  - `OK`

### Clean Linux hard gate

Full matrix:

- `PYTHONPATH=src:. python3 scripts/run_test_matrix.py --group full`
- result:
  - `293 tests`
  - `OK`
  - `1 skipped`

Skipped test:

- `tests.goal31_lsi_gap_closure_test.Goal31LsiGapClosureTest.test_frozen_k5_slice_is_parity_clean_when_local_snapshot_exists`
- skip reason:
  - `frozen k=5 exact-source snapshot is not available in this checkout`
- release interpretation:
  - this is a known fixture-availability skip, not a runtime or correctness
    failure on the release head

Focused milestone add-on slice:

- `PYTHONPATH=src:. python3 -m unittest ...`
- result:
  - `15 tests`
  - `OK`

Vulkan unit/backend slice:

- `make build-vulkan`
- `PYTHONPATH=src:. python3 -m unittest tests.rtdsl_vulkan_test tests.goal71_prepared_backend_positive_hit_county_test tests.goal69_pip_positive_hit_performance_test`
- result:
  - `23 tests`
  - `OK`

Goal 51 Vulkan validation:

- artifact:
  - `/Users/rl2025/rtdl_python_only/docs/reports/goal100_release_validation_rerun_artifacts_2026-04-05/goal51/summary.json`
- result:
  - all listed targets `parity: true`

Artifact provenance note:

- the Goal 51 JSON does not carry its own `validated_head` field
- its provenance in this package is established by the fresh clone path,
  the explicit rerun command, and its placement under the Goal 100 artifact
  directory

Fresh same-head OptiX repeated raw-input exact-source row:

- artifact:
  - `/Users/rl2025/rtdl_python_only/docs/reports/goal100_release_validation_rerun_artifacts_2026-04-05/optix_raw/summary.json`
- result:
  - parity preserved on all reruns
    - this is correctness parity, not a cold-run performance win
  - first run:
    - OptiX `7.045462893001968 s`
    - PostGIS `3.2089334549964406 s`
  - best repeated run:
    - OptiX `2.11339892099204 s`
    - PostGIS about `3.19-3.21 s`

Date note:

- the artifact JSON carries `2026-04-04` because that script wrote its own run
  date from the Linux host at execution time
- this Goal 100 report is dated `2026-04-05` because that is the packaging and
  review date for the release-validation package

Fresh same-head Embree prepared exact-source row:

- artifact:
  - `/Users/rl2025/rtdl_python_only/docs/reports/goal100_release_validation_rerun_artifacts_2026-04-05/embree_prepared/summary.json`
- result:
  - parity preserved on both reruns
  - run 1:
    - Embree `1.4399550010130042 s`
    - PostGIS `3.1524988659948576 s`
  - run 2:
    - Embree `1.0430747130012605 s`
    - PostGIS `3.099748136999551 s`

## Same-head artifact consistency checks

The release gate also checked the current same-head accepted artifacts already
published in Goals 98 and 99.

### OptiX prepared exact-source

Same-head artifact:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal99_optix_cold_prepared_run1_win_artifacts_2026-04-05/summary.json`

Accepted values:

- run 1:
  - OptiX `2.5369022019876866 s`
  - PostGIS `3.39459279399307 s`
  - parity `true`
- run 2:
  - OptiX `2.133376205994864 s`
  - PostGIS `3.01533580099931 s`
  - parity `true`

### OptiX parity repair package

Same-head artifacts:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal98_optix_release_regression_repair_artifacts_2026-04-05/prepared/summary.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal98_optix_release_regression_repair_artifacts_2026-04-05/raw/summary.json`

Accepted conclusion:

- prepared parity restored
- repeated raw-input parity restored

### Embree and Vulkan long-row position

No backend code affecting Embree or Vulkan changed between the already
published backend-closure goals and this rerun head.

Backend diff evidence between the earlier release candidate head and the
validated Goal 98/99 head:

- `git diff --name-only c43f538 e15ee77 -- src/rtdsl src/native`
- changed files:
  - `src/native/rtdl_optix.cpp`
  - `src/rtdsl/optix_runtime.py`

So the carry-forward applies only to backends whose runtime/native code did not
change across that range.

So the release gate carries forward the same-head accepted Embree raw and
Vulkan artifacts:

- Embree raw:
  - `/Users/rl2025/rtdl_python_only/docs/reports/goal83_embree_long_exact_source_repair_artifacts_2026-04-04/raw/summary.json`

- Vulkan:
  - `/Users/rl2025/rtdl_python_only/docs/reports/goal87_vulkan_long_exact_source_artifacts_2026-04-05/summary.json`
  - `/Users/rl2025/rtdl_python_only/docs/reports/goal88_vulkan_long_exact_raw_input_artifacts_2026-04-05/summary.json`

That carry-forward is intentional and explicit. It is not being presented as a
fresh rerun of those Vulkan long rows on the new clone.

## Pass/fail summary

- local preflight:
  - `pass`
- clean Linux full matrix:
  - `pass`
- focused Linux milestone slice:
  - `pass`
- Linux Vulkan slice:
  - `pass`
- Goal 51 Vulkan validation:
  - `pass`
- same-head OptiX repair/run-1 package consistency:
  - `pass`
- carried-forward backend provenance check:
  - `pass`

## Honest conclusion

Goal 100 succeeded as a release-validation rerun.

The current release head is healthy under a strong fresh-clone Linux test gate,
and the latest OptiX repair/win package is consistent with that rerun.

Important boundary:

- this is a high-signal release gate, not a promise that every previously
  published long-row backend benchmark was rerun again from scratch on the new
  clone
- where the gate carries forward already-published same-head backend artifacts,
  it says so explicitly

## Review closure

Goal 100 now has the required `3-AI` final-package review trail:

- Codex:
  - `/Users/rl2025/rtdl_python_only/history/ad_hoc_reviews/2026-04-05-codex-review-goal100-final-package.md`
- Gemini:
  - `/Users/rl2025/rtdl_python_only/history/ad_hoc_reviews/2026-04-05-gemini-review-goal100-final-package.md`
- Claude:
  - `/Users/rl2025/rtdl_python_only/history/ad_hoc_reviews/2026-04-05-claude-review-goal100-final-package.md`
  - rerun:
    - `/Users/rl2025/rtdl_python_only/history/ad_hoc_reviews/2026-04-05-claude-review-goal100-final-package-rerun.md`
- consensus:
  - `/Users/rl2025/rtdl_python_only/history/ad_hoc_reviews/2026-04-05-codex-consensus-goal100-final-package.md`
