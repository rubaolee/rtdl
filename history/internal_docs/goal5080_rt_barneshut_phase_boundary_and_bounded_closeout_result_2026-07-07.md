# Goal5080 RT-BarnesHut Phase Boundary And Bounded Closeout Result

Date: 2026-07-07

## Verdict Label

`completed_phase_boundary_analysis__bounded_same_input_correctness_closed__performance_claim_limited`

## Purpose

Goal5079 closed the live POD correctness gates for the app-neutral aggregate-hierarchy route. Goal5080 analyzes the timing phase boundary and decides what can be claimed now.

The key distinction is:

- **Correctness:** bounded same-input scalar force output is closed.
- **Performance:** the narrow force-kernel comparison is favorable to RTDL, but the broader reported envelope is not favorable to RTDL.
- **Paper reproduction:** full RT-BarnesHut paper reproduction remains unclosed because this is one bounded same-input route, not the full paper evaluation matrix.

## Evidence Inputs

Primary artifacts:

```text
Paper-reproduction-apps/rt-barneshut-paper/_runs/remote_full_pod_gate/g5079cont/pulled/_runs/full_pod_reproduction_gate/summary.json
Paper-reproduction-apps/rt-barneshut-paper/_runs/remote_full_pod_gate/g5079cont/pulled/_runs/generic_aggregate_force_same_input_gate/summary.json
Paper-reproduction-apps/rt-barneshut-paper/_runs/remote_full_pod_gate/g5079cont/pulled/_runs/same_input_rtdl_comparison_gate/summary.json
Paper-reproduction-apps/rt-barneshut-paper/_runs/remote_full_pod_gate/g5079cont/pulled/_runs/same_input_performance_gate/summary.json
```

The phase-review template was generated against the pulled Goal5079 timing summary:

```text
Paper-reproduction-apps/rt-barneshut-paper/_runs/remote_full_pod_gate/g5079cont/pulled/_runs/same_input_performance_gate/phase_boundary_review.json
Paper-reproduction-apps/rt-barneshut-paper/_runs/remote_full_pod_gate/g5079cont/pulled/_runs/phase_boundary_review_gate/summary.json
```

The generated phase-review gate remains blocked because no external human reviewer has accepted the phase boundary yet:

```text
status = blocked_review_incomplete_or_mismatched
performance_review_complete = false
phase_boundary_accepted = false
reviewed_ratio_matches_summary = true
reviewed_summary_path_matches = true
```

This is the correct state before external review.

## Correctness Status

### Full POD Gate

Goal5079 full gate:

```text
overall_status = passed_correctness_and_timing_gates__phase_boundary_review_required
```

All eight gates passed:

```text
local_contract_gate
author_source_contract_gate
pod_environment_preflight
author_contract_rtdl_cuda_gate
author_comparator_gate
generic_aggregate_force_same_input_gate
same_input_author_vs_rtdl_gate
same_input_performance_gate
```

### Generic Aggregate Route

The RTDL aggregate-hierarchy route matched the patched-author same-input scalar force file:

```text
generic_public_rtdl_api_used = true
opening.policy = continuation_payload_opening
force_count = 32768
matched = true
mismatch_count = 0
max_abs_error = 1830.0
max_rel_error = 2.1112736725325853e-06
rtol = 0.0001
atol = 0.0001
```

This supports a bounded correctness statement:

```text
RT-BarnesHut same-input scalar force output is reproduced against AuthorOfficial through an app-neutral RTDL aggregate-hierarchy route.
```

It does not support a full paper reproduction statement. It also should not be read as independent tree-construction proof: this is same-prepared-state plus payload-matched reproduction.

## Phase Boundary Analysis

### Narrow Force-Kernel Phase

The timing summary defines the narrow phase as:

```text
Author phase: author_treelogy_timing_ms.rt_core_force
RTDL phase:   rtdl_diagnostic_timing_ms.resident_kernel_min
```

Values:

```text
Author rt_core_force_ms       = 2.083
RTDL resident_kernel_min_ms   = 0.856544017791748
RTDL resident_kernel_mean_ms  = 0.9283008098602294
```

Ratios:

```text
RTDL min / Author rt_core_force  = 0.4112069216475026
RTDL mean / Author rt_core_force = 0.4456556936438931
```

Interpretation:

```text
On this POD run, in a narrow force-kernel phase comparison pending external phase-boundary acceptance, RTDL resident kernel timing is lower than the author reported RT-core force phase.
```

Required caveat:

```text
This is not a whole-program comparison. It excludes RTDL extension compilation, CPU prepared-array/tree processing, host-to-device tensor preparation, force-file output, and broader app orchestration.
```

### Broader Reported Envelope

RTDL reported components:

```text
extension_compile_ms          = 55.8721125125885
tree_prepare_cpu_ms           = 252.25137174129486
tensor_prepare_host_to_device_ms = 160.36569327116013
resident_kernel_min_ms        = 0.856544017791748
resident_kernel_mean_ms       = 0.9283008098602294
```

RTDL reported envelope:

```text
compile + tree_prepare + H2D + resident_kernel_min
= 469.34572154283524 ms

compile + tree_prepare + H2D + resident_kernel_mean
= 469.4174783349037 ms
```

Author reported broader timing:

```text
author preprocessing_ms = 18.804
author execution_ms     = 166.642
author preprocessing + execution = 185.44600000000003 ms
```

Broader envelope ratio:

```text
RTDL reported envelope min / Author preprocessing+execution
= 2.530902373428573

RTDL reported envelope mean / Author preprocessing+execution
= 2.5312893151370406
```

Interpretation:

```text
The broader reported envelope is not favorable to RTDL. Under this envelope, RTDL is about 2.53x slower than the author reported preprocessing+execution time.
```

## Claim Matrix

| Claim | Status | Evidence | Notes |
| --- | --- | --- | --- |
| Bounded same-input scalar force correctness | Authorized for review | generic route `mismatch_count = 0`; legacy diagnostic `mismatch_count = 0` | Same 32,768-body input and patched-author prepared arrays. |
| App-neutral RTDL aggregate-hierarchy route used | Authorized for review | `generic_public_rtdl_api_used = true`; `opening.policy = continuation_payload_opening` | App owns author-state parsing and force formatting. At Goal5080 close, `ContinuationPayloadOpening` is provisional generic until Goal5081 supplies non-RT-BarnesHut proof. |
| Narrow resident force-kernel ratio | Ready for external phase-boundary review | `0.4112069216475026` min ratio | Must be labeled narrow. |
| Whole-envelope RTDL speedup | Not authorized | broader envelope ratio `2.53x` slower | Explicitly unfavorable to RTDL. |
| Full RT-BarnesHut paper reproduction | Not authorized | only bounded same-input route closed | Full paper matrix and final completion audit still absent. |
| Broad RTDL performance claim | Not authorized | one bounded app route | No broad claim. |

## System Boundary

This goal preserves the same boundary established by Goals5063-5079:

- RTDL core provides generic aggregate hierarchy, opening, and reducer APIs.
- RT-BarnesHut app owns author prepared-state parsing, continuation sentinel normalization, scalar force-output formatting, author comparator, and POD orchestration.

`ContinuationPayloadOpening` is app-neutral because it is defined over continuation columns and a size/distance threshold. At the Goal5080 boundary it is provisional generic, not independently genericity-proven, because the live consumer is RT-BarnesHut. Goal5081 adds the required non-RT-BarnesHut consumer proof. The app-specific author binary sentinel handling remains outside RTDL core.

## Decision

Goal5080 should close as:

```text
bounded same-input correctness: closed
narrow force-kernel phase: ready for external review
whole-envelope performance: not favorable to RTDL
full paper reproduction: not closed
```

## Next Recommended Step

Send this report and Goal5079 to external review.

If the external reviewer accepts the narrow phase boundary, a later goal may set a reviewed phase artifact to:

```text
performance_review_complete = true
phase_boundary_accepted = true
```

Even then, the accepted claim must remain narrow unless a separate completion audit and paper-scope review approve more.
