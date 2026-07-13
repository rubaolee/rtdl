# Call For Review - Goal5264 X-HD hd_exec Graphics Dragon/AsianDragon Entrypoint

Date: 2026-07-09

## Review Scope

Please strictly review Goal5264, which runs the Stanford Graphics Dragon ->
AsianDragon scaled same-source candidate through the RTDL `hd_exec`-compatible
user entrypoint.

Primary result:

```text
history/internal_docs/goal5264_xhd_hd_exec_graphics_dragon_asian_entrypoint_result_2026-07-09.md
```

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5264_dragon_asian_hd_exec_exact_witness_pod.json
```

Test:

```text
tests/goal5264_xhd_hd_exec_graphics_dragon_asian_pod_artifact_test.py
```

Related author comparator:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5239_dragon_asian_scaled_same_pod_performance_matrix_2026-07-09.json
```

## Claims To Verify

1. The RTDL `hd_exec`-compatible entrypoint can run the Stanford Graphics
   Dragon -> AsianDragon scaled candidate through the exact-witness route.

2. The route matches the Goal5239 author rerun `HDResult` within `1e-6`:

```text
author_hd_result = 0.06536787003278732
RTDL HDResult = 0.06536787240753439
abs_diff = 2.3747470656587666e-09
```

3. The result keeps the paper-log drift visible:

```text
paper_log_hd_result = 0.06536811590194702
rtdl_vs_paper_log_abs_diff ~= 2.4349441263282756e-07
```

4. Point counts and preprocessing align with the Level-B same-source/scaled
   candidate contract:

```text
point_count_a = 437645
point_count_b = 3609600
preprocessing = translate_each_input_to_min_bound
```

5. The exact-witness route reports:

```text
route_label = cell-mbr-exact-witness
per_source_witness_exact = true
RTDL route wall ~= 2651.05 ms
```

6. README and manifest include Goal5264 while preserving the claim boundary.

7. No forbidden claim is introduced:

```text
exact paper byte-input identity
full X-HD paper reproduction
Figure reproduction
author RT-core algorithm equivalence
author performance parity or speedup
same-source/scaled candidate equals exact paper dataset
```

## Review Questions

1. Does Goal5264 legitimately extend the `hd_exec`-compatible entrypoint to a
   second Stanford Graphics representative workload?
2. Is comparing against Goal5239 author rerun `HDResult` the correct Level-B
   same-source/scaled candidate comparator?
3. Does the paper-log drift remain visible enough to prevent an exact-paper
   dataset claim?
4. Is `per_source_witness_exact=true` supported by the exact-witness route
   artifact?
5. Are the route-wall numbers safely labeled as RTDL route diagnostics without
   turning into an author performance parity claim?
6. Does uploading the scaled public candidate to the POD preserve provenance,
   given the Goal5234 SHA and scale record?
7. Can Goal5264 be closed as a user-entrypoint graphics representative gate?

## Expected Verdict Labels

Preferred approval:

```text
approve_goal5264_xhd_hd_exec_graphics_dragon_asian_entrypoint
```

Possible amendment:

```text
revise_goal5264_due_to_scaled_candidate_or_paper_log_boundary
```

Possible block:

```text
block_goal5264_due_to_invalid_author_comparator_or_overclaimed_exact_dataset
```

Please provide:

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to review questions:
```
