# Call For Review - Goal5265 X-HD hd_exec Graphics ThaiStatuette/HappyBuddha Entrypoint

Date: 2026-07-09

## Review Scope

Please strictly review Goal5265, which acquires/scales public Stanford
ThaiStatuette and runs ThaiStatuette -> HappyBuddha through the RTDL
`hd_exec`-compatible user entrypoint.

Primary result:

```text
history/internal_docs/goal5265_xhd_hd_exec_graphics_thai_happy_entrypoint_result_2026-07-09.md
```

Artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5265_thai_statuette_scaled_1e-3_candidate_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5265_author_thai_happy_scaled_rt_gpu_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5265_thai_happy_hd_exec_exact_witness_pod.json
```

Test:

```text
tests/goal5265_xhd_hd_exec_graphics_thai_happy_pod_artifact_test.py
```

Related paper-log source:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_branch_log_index_goal5176_2026-07-08.json
```

## Claims To Verify

1. ThaiStatuette was acquired from the public Stanford XYZRGB source and scaled
   by an app-owned `1e-3` step that matches paper-log coordinate scale:

```text
raw vertex_count = 4999996
scaled coordinate_extents = [0.2352239456, 0.39604121399, 0.20316127014]
```

2. Author `hd_exec` rerun on ThaiStatuette scaled -> HappyBuddha matches the
   paper-branch log value within `1e-6`:

```text
paper_log_HDResult = 0.21912434697151184
author_rerun_HDResult = 0.21912431716918945
abs_diff ~= 2.98e-8
```

3. RTDL `hd_exec`-compatible exact-witness route matches author rerun within
   `1e-6`:

```text
RTDL HDResult = 0.2191243235042005
abs(RTDL - author rerun) ~= 6.34e-9
per_source_witness_exact = true
```

4. The route-wall number is denominator-labeled only:

```text
RTDL route wall ~= 5013.23 ms
author Running.AvgTime = 26.664 ms
```

No performance parity or speedup claim is authorized.

5. README / manifest / Stanford external-data README include Goal5265 while
   preserving the claim boundary.

6. No forbidden claim is introduced:

```text
exact paper byte-input identity
full X-HD paper reproduction
Figure reproduction
author RT-core algorithm equivalence
author performance parity or speedup
scaled public candidate equals exact paper dataset
```

## Review Questions

1. Is the public ThaiStatuette acquisition/provenance sufficient for Level-B
   same-source evidence?
2. Is the `1e-3` scaled candidate justified by the paper-branch MBR scale, while
   still not becoming Level-C exact paper identity?
3. Is author rerun on scaled Thai -> Happy the correct comparator for this
   user-entrypoint graphics gate?
4. Does the RTDL exact-witness route support the correctness claim?
5. Are performance numbers safely denominator-labeled?
6. Do docs and manifest avoid overclaiming full paper reproduction or exact
   paper inputs?
7. Can Goal5265 be closed as another user-entrypoint graphics representative
   gate?

## Expected Verdict Labels

Preferred approval:

```text
approve_goal5265_xhd_hd_exec_graphics_thai_happy_entrypoint
```

Possible amendment:

```text
revise_goal5265_due_to_scaled_candidate_or_performance_boundary
```

Possible block:

```text
block_goal5265_due_to_invalid_scaling_or_overclaimed_exact_dataset
```

Please provide:

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to review questions:
```
