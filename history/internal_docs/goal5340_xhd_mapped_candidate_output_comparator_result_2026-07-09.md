# Goal5340 - X-HD Mapped-Candidate Output Comparator Result

Date: 2026-07-09

Status: `implemented_review_pending`

Exit label: `mapped_candidate_same_input_output_comparator_ready__await_real_pod_outputs`

## Purpose

Goal5340 adds the app-owned post-execution comparator for the mapped-candidate
same-input gate prepared by Goal5339.

It reads a Goal5339 command packet after a later POD goal has executed the
author and RTDL commands, loads the expected author and RTDL JSON outputs,
compares `HDResult` with an explicit tolerance, and preserves timing fields as
separate evidence.

This goal does not execute the commands, does not use POD, and does not claim
exact paper dataset identity, Figure 5 reproduction, full X-HD paper
reproduction, or author-vs-RTDL performance ratio.

## Files Added

```text
Paper-reproduction-apps/x-hd-paper/scripts/compare_xhd_mapped_candidate_same_input_outputs.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5340_mapped_candidate_output_comparison.json
tests/goal5340_xhd_mapped_candidate_output_comparator_test.py
```

## Comparator Contract

Input:

```text
Goal5339 mapped-candidate same-input gate packet JSON
author JSON output produced by a later POD execution
RTDL JSON output produced by a later POD execution
```

Output schema:

```text
rtdl.paper_reproduction.xhd.mapped_candidate_same_input_output_comparison.v1
```

The comparator emits one of:

```text
mapped_candidate_same_input_gate_passed
mapped_candidate_same_input_gate_failed
mapped_candidate_outputs_missing
packet_not_ready_for_output_comparison
```

`mapped_candidate_same_input_gate_passed` requires:

```text
packet classification == mapped_candidate_same_input_gate_commands_ready
author JSON exists
RTDL JSON exists
author HDResult finite
RTDL HDResult finite
abs(author HDResult - RTDL HDResult) <= explicit tolerance
```

## Timing Treatment

The comparator intentionally keeps timing fields separated:

```text
author_timing:
  Running.AvgTime
  Running.Repeats[].ReportedTime values and median
  semantics: author hd_exec internal timing fields

rtdl_timing:
  Running.AvgTime
  RTDL.route_label
  RTDL.run_phases
  semantics: RTDL route/run timing as reported by the RTDL runner
```

It always reports:

```text
performance_ratio_reported = false
```

Reason: even after `HDResult` matches, author internal timing and RTDL route or
runner timing are different denominators until a separate phase-boundary and
hardware-alignment goal proves otherwise.

## Validation

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5340_mapped_candidate_output_comparison.json
json.tool OK

py -m unittest tests.goal5340_xhd_mapped_candidate_output_comparator_test
Ran 5 tests OK

py -m unittest tests.goal5339_xhd_mapped_candidate_same_input_packet_test tests.goal5340_xhd_mapped_candidate_output_comparator_test
Ran 9 tests OK
```

The local Python environment prints:

```text
Could not find platform independent libraries <prefix>
```

This is the known Windows `py` noise and did not prevent the tests from
passing.

## Test Coverage

The focused tests cover:

```text
matching author/RTDL HDResult passes without performance ratio
HDResult mismatch fails the gate
missing author/RTDL outputs fail the gate
packet not command-ready fails the gate
summary forbids exact/full/performance claims
```

The tests synthesize a Goal5337 -> Goal5338 -> Goal5339 chain and then feed the
Goal5340 comparator. This proves the comparator's control-flow and claim
boundaries without requiring real ACM artifacts or POD execution.

## POD Usage

```text
used = false
expected_next = false
reason = local post-execution comparator only; real command execution belongs
         to a later POD goal after accepted mapping and materialized candidate
         files exist.
```

## Claim Boundary

Allowed:

```text
Goal5340 adds an app-owned post-execution comparator for future mapped-candidate
same-input POD outputs.
It compares HDResult with explicit tolerance.
It keeps author and RTDL timing fields separated.
It reports no performance ratio.
```

Not allowed:

```text
claiming commands were executed by this comparator
claiming same-input correctness before real outputs exist
claiming exact paper dataset reproduction from an HDResult match alone
claiming Figure 5 reproduction from this comparison alone
claiming full X-HD paper reproduction from this comparison alone
claiming author-vs-RTDL performance ratio from this comparison
```

## Current Position

The X-HD external-provenance chain now has local tooling for:

```text
artifact inspection
artifact instruction ingestion
candidate bytes/hash mapping
candidate workload mapping review
same-input command packet construction
post-execution HDResult comparison
```

This is readiness infrastructure. It does not remove the exact-input blocker.
The next evidence-producing POD goal is authorized only after a real ACM/author
artifact is available, candidate files are materialized, and a clean accepted
workload mapping produces a command-ready Goal5339 packet.
