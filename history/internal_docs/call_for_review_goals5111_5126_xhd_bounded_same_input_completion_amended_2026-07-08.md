# Call For Review - Goals5111-5126 X-HD Bounded Same-Input Completion, Amended

Date: 2026-07-08

Please strictly review the X-HD paper-app completion packet for Goals5111-5126.

This amended packet responds to the prior required amendment:

```text
RA-1 directed semantics lacks discriminating evidence.
```

Goal5126 adds a directed-asymmetric fixture where `directed_a_to_b=0.5`,
`directed_b_to_a=9.0`, and symmetric diagnostic `hausdorff=9.0`, so a mistaken
symmetric comparator would fail.

Goal5110 has already been externally reviewed and approved. Goals5111-5125 are
implemented but intentionally **not** treated as approved until this consolidated
review is complete.

## Files To Review

Primary closeout:

```text
history/internal_docs/goal5125_xhd_bounded_same_input_closeout_2026-07-08.md
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
Paper-reproduction-apps/x-hd-paper/README.md
Paper-reproduction-apps/x-hd-paper/data/manifest.json
Paper-reproduction-apps/x-hd-paper/results/README.md
```

Goal reports:

```text
history/internal_docs/goal5111_xhd_tiny_same_input_author_json_gate_packet_2026-07-07.md
history/internal_docs/goal5112_xhd_author_hd_exec_build_run_attempt_2026-07-07.md
history/internal_docs/goal5113_xhd_bounded2d_same_input_author_json_gate_2026-07-08.md
history/internal_docs/goal5114_xhd_bounded3d_same_input_author_json_gate_2026-07-08.md
history/internal_docs/goal5115_xhd_bounded2d_rtdl_route_gate_2026-07-08.md
history/internal_docs/goal5116_xhd_completion_boundary_and_phase_model_2026-07-08.md
history/internal_docs/goal5117_generic_3d_hausdorff_column_route_contract_2026-07-08.md
history/internal_docs/goal5118_xhd_bounded3d_rtdl_route_gate_2026-07-08.md
history/internal_docs/goal5119_xhd_phase_semantics_and_author_contract_2026-07-08.md
history/internal_docs/goal5120_xhd_style_decision_route_feasibility_2026-07-08.md
history/internal_docs/goal5121_xhd_representative_dataset_decision_2026-07-08.md
history/internal_docs/goal5122_xhd_representative_correctness_gate_skipped_2026-07-08.md
history/internal_docs/goal5123_xhd_fair_performance_matrix_2026-07-08.md
history/internal_docs/goal5124_xhd_system_api_extraction_2026-07-08.md
history/internal_docs/goal5126_xhd_directed_semantics_discriminating_gate_amendment_2026-07-08.md
```

Result artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/tiny2d_author_gate_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/directed2d_asymmetric_author_gate_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/directed2d_asymmetric_author_hd_exec_output_pod.json
Paper-reproduction-apps/x-hd-paper/results/bounded2d_author_gate_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/bounded3d_author_gate_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/directed2d_asymmetric_rtdl_route_gate_summary.json
Paper-reproduction-apps/x-hd-paper/results/bounded2d_rtdl_route_gate_summary.json
Paper-reproduction-apps/x-hd-paper/results/bounded3d_rtdl_route_gate_summary.json
Paper-reproduction-apps/x-hd-paper/results/xhd_bounded_performance_matrix_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_author_build_patch_goal5112.diff
```

Key implementation files:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_author_json_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_route_gate.py
src/rtdsl/partner_continuations.py
src/rtdsl/__init__.py
tests/goal5110_xhd_paper_app_scaffold_test.py
tests/goal5111_xhd_author_json_gate_test.py
tests/goal5113_xhd_bounded2d_author_gate_test.py
tests/goal5114_xhd_bounded3d_author_gate_test.py
tests/goal5115_xhd_rtdl_route_gate_test.py
tests/goal5117_generic_3d_hausdorff_column_route_test.py
tests/goal5118_xhd_bounded3d_rtdl_route_gate_test.py
```

## Claimed Final Status

```text
xhd_bounded_same_input_reproduction_complete__pending_external_review
```

This means:

- bounded same-input correctness is complete as an implementation packet;
- exact paper dataset reproduction is not claimed;
- representative same-source reproduction is not claimed;
- performance parity or speedup is not claimed;
- the packet still requires external review before dropping the
  `pending_external_review` suffix.

## Summary Of Evidence

Correctness gates:

```text
tiny2d:
  author HDResult = 1.0
  directed input1->input2 reference = 1.0
  matched = true

bounded2d:
  author HDResult = 2.0
  directed input1->input2 reference = 2.0
  RTDL public 2D column route = 2.0
  matched = true

bounded3d:
  author HDResult = 2.0
  directed input1->input2 reference = 2.0
  RTDL public 3D column route = 2.0
  matched = true

directed2d_asymmetric:
  author HDResult = 0.5
  directed input1->input2 reference = 0.5
  directed input2->input1 diagnostic = 9.0
  symmetric diagnostic = 9.0
  RTDL public 2D column route directed comparison = 0.5
  matched = true
```

System extraction:

```text
new generic RTDL API:
  point_rows_to_numpy_columns_3d
  directed_hausdorff_3d_numpy_columns

non-X-HD genericity proof:
  tests/goal5117_generic_3d_hausdorff_column_route_test.py
```

Performance boundary:

```text
author bounded2d retained Running.AvgTime = 3.873 ms
author bounded2d process wall median = 1.079 s
RTDL local bounded2d route phase = 0.00142 s

author bounded3d retained Running.AvgTime = 4.235 ms
author bounded3d process wall median = 1.104 s
RTDL local bounded3d route phase = 0.00159 s

No ratio is reported because denominators/hardware/algorithm phases do not align.
```

Dataset boundary:

```text
author repo logs reference /local/storage/shared/HDDatasets
current POD does not contain that data root
exact paper inputs unavailable
Goal5122 representative gate skipped
```

## Local Verification Already Run

```text
py -m unittest \
  tests.goal5110_xhd_paper_app_scaffold_test \
  tests.goal5111_xhd_author_json_gate_test \
  tests.goal5113_xhd_bounded2d_author_gate_test \
  tests.goal5114_xhd_bounded3d_author_gate_test \
  tests.goal5115_xhd_rtdl_route_gate_test \
  tests.goal5117_generic_3d_hausdorff_column_route_test \
  tests.goal5118_xhd_bounded3d_rtdl_route_gate_test

Ran 21 tests in 1.129s
OK
```

Claim scan note:

```text
Positive forbidden-claim scan found only forbidden/not-claimed lists in README
and manifest; no positive author-parity, speedup, exact-paper, or full-paper
claim was found.
```

## Review Questions

1. Does the packet correctly fix the earlier plan issue by treating Goals5111-5115
   as implemented/review-pending rather than already externally approved?
2. Is the final status `xhd_bounded_same_input_reproduction_complete__pending_external_review`
   honest for the evidence presented?
3. Does Goal5126 close the previous directed/symmetric required amendment by
   adding a discriminating fixture where directed input1-to-input2 differs from
   the symmetric Hausdorff max?
4. Are the tiny2d, bounded2d, and bounded3d author gates sufficient for bounded
   same-input correctness under the stated tolerance?
5. Does the bounded2d/bounded3d RTDL route use generic public RTDL columnar APIs
   rather than app-specific X-HD core primitives?
6. Is the new 3D route (`point_rows_to_numpy_columns_3d`,
   `directed_hausdorff_3d_numpy_columns`) sufficiently app-neutral, including
   the non-X-HD synthetic test?
7. Is Goal5120's conclusion correct: existing generic 2D fixed-radius threshold
   support can express a Hausdorff decision subproblem, but full author-style
   X-HD iterative RT route requires new generic API and is not closed here?
8. Is Goal5121's dataset decision acceptable: author logs reference external
   datasets, but exact paper/same-source inputs are unavailable in current
   evidence, so Goal5122 is skipped?
9. Is the performance matrix disciplined: phase disclosure only, no speedup
   ratio, no parity claim, no mixing author `Running.AvgTime` with process wall
   or local RTDL route time?
10. Does the app/system boundary hold: author wrapper/comparator/fixtures/tolerance
    stay app-owned, while only generic Hausdorff column operations enter RTDL?
11. Are there any remaining public-surface or manifest overclaims?
12. If approved, may the status be updated from
    `xhd_bounded_same_input_reproduction_complete__pending_external_review` to
    `xhd_bounded_same_input_reproduction_complete`?

## Requested Output Shape

Please answer with:

```text
Verdict:
  approve_xhd_goals5111_5126_bounded_same_input_completion
  OR approve_with_required_amendments
  OR revise_before_closeout

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Answers to the 12 review questions:
  1. ...
  ...
  12. ...
```
