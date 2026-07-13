# Call For Review - Goal5289 X-HD Figure 5 Bounded Same-POD Probe

Date: 2026-07-09

## Review Scope

Please strictly review Goal5289, which runs one bounded same-POD Figure 5
graphics candidate under author `hd_exec` and RTDL `hd_exec`-compatible entrypoint.

This is a no-go probe. It is not a Figure 5 reproduction claim and not a
performance ratio.

## Files To Review

```text
history/internal_docs/goal5289_xhd_figure5_bounded_same_pod_probe_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5289_figure5_bounded_same_pod_probe_2026-07-09.json
tests/goal5289_xhd_figure5_bounded_same_pod_probe_test.py
```

Relevant prior evidence:

```text
history/internal_docs/goal5288_xhd_figure5_timing_denominator_audit_result_2026-07-09.md
history/internal_docs/goal5269_xhd_figure6_lb256_correctness_probe_result_2026-07-09.md
history/internal_docs/goal5270_xhd_figure6_exact_input_availability_decision_result_2026-07-09.md
```

## Evidence Summary

POD:

```text
NVIDIA RTX 4000 Ada Generation
```

Input:

```text
dragon.ply -> asian_dragon_scaled_1e-3.ply
Level-B public/same-source candidate
```

Author:

```text
variant=rt, execution=gpu, EB=true, Prune=true, LB=256
HDResult = 0.06545527279376984
Running.AvgTime = 18.436 ms
process wall ~= 2.095 s
```

RTDL:

```text
route = cell-mbr-fast-scalar
HDResult = 0.06536787240753439
process wall ~= 261.970 s
```

Decision:

```text
matched_value = false
abs_diff ~= 8.74e-05
same_denominator_ratio_allowed = false
figure5_reproduced = false
```

## Review Questions

1. Is the same-POD probe evidence real and correctly scoped as bounded
   Level-B, not exact paper input?
2. Is it correct that the author run uses the paper-like X-HD/LB=256 default?
3. Is it correct that the author and RTDL HDResult values do not match within
   the stated tolerance?
4. Is it correct to forbid a Figure 5 performance ratio from this probe?
5. Does this reproduce the same LB=256 candidate mismatch pattern seen in the
   Figure 6 diagnostics?
6. Does the report avoid Figure 5 reproduction, exact input, and performance
   parity claims?
7. Can Goal5289 be marked externally reviewed and approved as a no-go probe, or
   are amendments required?

## Expected Answer Shape

```text
Verdict: approve / approve_with_required_amendments / block
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to questions 1-7:
Requested verdict label:
```

If approving, please use or adapt:

```text
approve_goal5289_xhd_figure5_bounded_same_pod_probe_no_go
```
