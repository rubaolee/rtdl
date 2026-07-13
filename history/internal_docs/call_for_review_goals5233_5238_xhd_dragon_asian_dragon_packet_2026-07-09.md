# Call For Review: Goals5233-5238 X-HD Dragon -> AsianDragon Packet

Please strictly review the X-HD Dragon -> AsianDragon packet from Goals5233
through 5238.

This is a significant packet: it moves from a raw public candidate that does
not match the paper log, through a scaled public candidate that matches the
author HDResult, through bounded RTDL route gates, to an all-source RTDL
route-only match against the author scaled-public HDResult, and finally to an
author-source audit proving the required PLY min-bound translation contract.

## Files To Review

```text
history/internal_docs/goal5233_graphics_dragon_asian_dragon_subset_route_gate_result_2026-07-09.md
history/internal_docs/goal5234_graphics_dragon_asian_dragon_scaled_author_gate_result_2026-07-09.md
history/internal_docs/goal5235_graphics_dragon_asian_dragon_scaled_subset_scaling_matrix_result_2026-07-09.md
history/internal_docs/goal5236_graphics_dragon_asian_dragon_scaled_optix_pod_bounded_gate_result_2026-07-09.md
history/internal_docs/goal5237_graphics_dragon_asian_dragon_scaled_all_source_route_only_result_2026-07-09.md
history/internal_docs/goal5238_xhd_author_ply_loader_translation_contract_result_2026-07-09.md

history/internal_docs/call_for_review_goal5233_graphics_dragon_asian_dragon_subset_route_gate_2026-07-09.md
history/internal_docs/call_for_review_goal5234_graphics_dragon_asian_dragon_scaled_author_gate_2026-07-09.md
history/internal_docs/call_for_review_goal5235_graphics_dragon_asian_dragon_scaled_subset_scaling_matrix_2026-07-09.md
history/internal_docs/call_for_review_goal5236_graphics_dragon_asian_dragon_scaled_optix_pod_bounded_gate_2026-07-09.md
history/internal_docs/call_for_review_goal5237_graphics_dragon_asian_dragon_scaled_all_source_route_only_2026-07-09.md
history/internal_docs/call_for_review_goal5238_xhd_author_ply_loader_translation_contract_2026-07-09.md
```

Key evidence artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5234_author_dragon_asian_raw_public_gate_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5234_author_dragon_asian_scaled_1e-3_public_gate_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5235_graphics_dragon_asian_dragon_scaled_subset_scaling_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5236_graphics_dragon_asian_dragon_scaled_subset256_optix_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5236_graphics_dragon_asian_dragon_scaled_subset1024_optix_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5237_graphics_dragon_asian_dragon_scaled_all_source_optix_route_only_translated_no_global_early_break_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5237_graphics_dragon_asian_dragon_scaled_all_source_optix_route_only_translated_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5237_graphics_dragon_asian_dragon_scaled_all_source_optix_route_only_no_translate_pod_2026-07-09.json
tests/goal5238_xhd_author_ply_loader_translation_contract_test.py
```

## Claimed Chain

### Goal5233

Generalized the X-HD public route bridge beyond hard-coded Dragon -> HappyBuddha
and added app-owned binary PLY loading for Stanford binary-big-endian inputs.
The raw public Dragon -> AsianDragon 16-source route matched exact subset
oracle, but raw public AsianDragon did not match the paper-log scale.

### Goal5234

Established the app-owned scaled public candidate:

```text
asian_dragon.ply -> asian_dragon_scaled_1e-3.ply
scale = 0.001
```

Author comparison:

```text
raw public author HDResult = 52.453487396240234
paper-log HDResult = 0.06536811590194702
raw matched = false

scaled public author HDResult = 0.06536787003278732
paper-log HDResult = 0.06536811590194702
scaled diff = 2.4586915969848633e-07
scaled matched = true
```

### Goal5235

Ran local bounded scaled RTDL routes for source limits 16, 64, and 256 against
the full scaled target. All matched exact subset oracle with `route_abs_diff=0`.

### Goal5236

Uploaded current source to the POD, rebuilt `librtdl_optix.so`, and ran bounded
OptiX gates for 256 and 1024 source points. Both matched exact subset oracle:

```text
256-source route_abs_diff = 0.0
1024-source route_abs_diff = 0.0
```

This fixed the old-POD-snapshot concern.

### Goal5237

Ran the full source set with route-only author comparison.

Successful mode:

```text
preprocessing = translate_each_input_to_min_bound
global_bound_early_break = false
source_count = 437,645
target_count = 3,609,600
RTDL route distance = 0.06536787240753439
author scaled HDResult = 0.06536787003278732
author_abs_diff = 2.3747470656587666e-09
matched = true
per_source_witness_exact = true
```

Diagnostic no-go modes:

```text
no translate:
  matched = false
  route distance = 0.1597462345977575

translate + global_bound_early_break:
  matched = false
  route distance = 0.06647010360490425
  per_source_witness_exact = false
```

### Goal5238

Audited the author source and found that `--input-type ply` dispatches to
`LoadPLY`, and `LoadPLY` independently subtracts each input's per-axis `vmin`:

```cpp
v[i] = (v[i] - vmin[i]);
```

Therefore the successful Goal5237 `translate_each_input_to_min_bound` mode is
not arbitrary RTDL normalization. It mirrors the author PLY loader's
app-owned input preprocessing contract.

## Review Questions

1. Does Goal5234 correctly establish that raw public AsianDragon is the wrong
   coordinate scale and that the scaled `0.001` candidate matches author
   paper-log HDResult within `1e-6`?
2. Does Goal5236 sufficiently prove current-source rebuilt OptiX evidence, not
   old POD snapshot evidence?
3. Do the Goal5236 bounded OptiX gates prove exact scalar and final witness
   agreement against exact subset oracles for source limits 256 and 1024?
4. Does Goal5237 prove an all-source route-only match against the author
   scaled-public HDResult?
5. Is the successful Goal5237 mode correctly constrained to
   `translate_each_input_to_min_bound=true` and
   `global_bound_early_break=false`?
6. Does Goal5238 settle that independent min-bound translation is an app-owned
   author-compatible PLY loader contract?
7. Does the global-bound early-break no-go correctly prevent using that mode
   for exact-value all-source reproduction claims?
8. Does the packet maintain the boundary that exact paper input byte identity
   is still unproved?
9. Does the packet avoid claiming Figure 6 reproduction and author-vs-RTDL
   performance parity?
10. What should be the next required work: performance denominator alignment,
    exact input byte-provenance, or another paper workload?

## Expected Answer Shape

```text
Verdict:
  approve_goals5233_5238_xhd_dragon_asian_dragon_packet
  OR approve_with_required_amendments
  OR block

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Answers to review questions:
  1. ...
  2. ...
```

## Forbidden Summaries

Please reject any summary that says:

```text
X-HD full paper reproduction is complete.
Exact paper input byte identity is proved.
Figure 6 is reproduced.
RTDL matches author performance.
Global-bound early break is exact for all-source reproduction.
Raw public AsianDragon matches the paper log.
The all-source result works without translation.
Translation is an RTDL core semantic.
```

## Allowed Summary Shape

The strongest allowed summary is:

```text
For the Dragon -> AsianDragon graphics workload, RTDL now matches the author
scaled-public all-source HDResult in route-only mode under a documented
same-source candidate contract: public AsianDragon scaled by 0.001,
independent min-bound translation matching the author PLY loader, and
global-bound early break disabled. This is Level-B same-source evidence, not
exact paper input identity, not Figure 6, and not performance parity.
```
