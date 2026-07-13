# Call For Review: Goal5238 X-HD Author PLY Loader Translation Contract

Please strictly review Goal5238.

## Files To Review

```text
history/internal_docs/goal5238_xhd_author_ply_loader_translation_contract_result_2026-07-09.md
tests/goal5238_xhd_author_ply_loader_translation_contract_test.py

history/internal_docs/goal5237_graphics_dragon_asian_dragon_scaled_all_source_route_only_result_2026-07-09.md
```

## Context

Goal5237 found:

```text
no translate: matched=false
translate + global_bound_early_break: matched=false
translate + no global_bound_early_break: matched=true
```

The main unresolved question was whether `translate_each_input_to_min_bound` is
a legitimate author-compatible preprocessing contract or an arbitrary RTDL
route normalization.

Goal5238 audits the author X-HD source and finds that `LoadPLY` independently
subtracts the per-axis minimum for each PLY input.

## Claims Under Review

1. Author `--input-type ply` dispatches to `LoadPLY` for both inputs.
2. Author `LoadPLY` subtracts each input's per-axis `vmin` from every vertex.
3. RTDL's `translate_point_matrix_to_min_bound` mirrors that author loader
   contract.
4. This preprocessing remains app-owned and does not become RTDL core semantics.
5. Goal5238 explains the Goal5237 no-translate failure without overclaiming
   exact paper byte identity or Figure 6 reproduction.

## Review Questions

1. Does the quoted author source prove the PLY min-bound translation contract?
2. Is the distinction from optional `--normalize` and `--translate` flags clear?
3. Does RTDL's app helper implement the same per-input per-axis min-bound
   subtraction?
4. Is the new unit test sufficient for app-side regression coverage?
5. Does Goal5238 avoid turning an app-owned author loader behavior into a
   generic RTDL semantic?
6. Does Goal5238 properly narrow the interpretation of Goal5237?
7. What should be next: fair performance matrix for this all-source workload,
   another paper workload, or exact input byte-provenance work?

## Expected Answer Shape

```text
Verdict:
  approve_goal5238_author_ply_loader_translation_contract
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

Reject any summary that says:

```text
translation proves exact paper input byte identity
translation is an RTDL core semantic
Goal5237 reproduces Figure 6
global-bound early break is exact
full X-HD paper reproduction is complete
```
