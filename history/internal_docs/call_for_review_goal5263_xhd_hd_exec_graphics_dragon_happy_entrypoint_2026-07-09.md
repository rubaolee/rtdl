# Call For Review - Goal5263 X-HD hd_exec Graphics Dragon/HappyBuddha Entrypoint

Date: 2026-07-09

## Review Scope

Please strictly review Goal5263, which runs the full-public Stanford Graphics
Dragon -> HappyBuddha Level-B representative pair through the RTDL
`hd_exec`-compatible user entrypoint.

Primary result:

```text
history/internal_docs/goal5263_xhd_hd_exec_graphics_dragon_happy_entrypoint_result_2026-07-09.md
```

Artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5263_dragon_happy_hd_exec_fast_scalar_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5263_dragon_happy_hd_exec_exact_witness_pod.json
```

Test:

```text
tests/goal5263_xhd_hd_exec_graphics_dragon_happy_pod_artifact_test.py
```

Related author comparator:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_author_gate_summary_goal5186_graphics_dragon_happy_buddha_2026-07-08.json
```

## Claims To Verify

1. The RTDL `hd_exec`-compatible entrypoint can run full-public Stanford PLY
   graphics input, not only WKT fixtures or ModelNet40 OFF files.
2. Both route labels match the Goal5186 author rerun HDResult within 1e-6:

```text
author_hd_result = 0.12572988867759705
RTDL HDResult = 0.12572988629271128
abs_diff = 2.3848857610975216e-09
```

3. Point counts and preprocessing align with the Goal5186 Level-B contract:

```text
point_count_a = 437645
point_count_b = 543652
preprocessing = translate_each_input_to_min_bound
```

4. The two route labels are correctly distinguished:

```text
cell-mbr-fast-scalar: per_source_witness_exact = false
cell-mbr-exact-witness: per_source_witness_exact = true
```

5. The README and manifest include the Goal5263 artifacts while preserving the
claim boundary.

6. No forbidden claim is introduced:

```text
exact paper byte-input identity
full X-HD paper reproduction
Figure reproduction
author RT-core algorithm equivalence
author performance parity or speedup
```

## Review Questions

1. Does Goal5263 legitimately extend the `hd_exec`-compatible entrypoint from
   ModelNet40/OFF to Stanford Graphics/PLY?
2. Is comparing against Goal5186 author rerun HDResult the correct Level-B
   same-source representative comparator?
3. Is it safe to report both route labels, given that fast-scalar has
   approximate/aborted per-source witnesses while exact-witness is exact?
4. Are the route-wall numbers acceptable as route timings without turning them
   into an author performance ratio?
5. Does uploading public PLY files to the POD preserve provenance, or is more
   hash evidence needed in this goal?
6. Can Goal5263 be closed as a user-entrypoint graphics representative gate?

## Expected Verdict Labels

Preferred approval:

```text
approve_goal5263_xhd_hd_exec_graphics_dragon_happy_entrypoint
```

Possible amendment:

```text
revise_goal5263_due_to_graphics_entrypoint_claim_boundary
```

Possible block:

```text
block_goal5263_due_to_invalid_author_comparator_or_overclaimed_exact_dataset
```

Please provide:

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to review questions:
```
