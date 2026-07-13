# Call For Review - Goal5229 ModelNet40 Author-Float32 Normalization

Please strictly review Goal5229.

## Files To Review

```text
history/internal_docs/goal5229_modelnet40_author_float32_normalization_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/xhd_input_loader.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_modelnet40_normalized_batch_gate.py
tests/goal5219_xhd_off_normalize_input_contract_test.py
tests/goal5223_modelnet40_algorithm_aware_comparator_test.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5229_modelnet40_all400_float32norm_aggregate_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5229_modelnet40_all400_float32norm_case_artifacts_2026-07-09.tar.gz
```

## Context

Goal5227 ran all 400 unique ModelNet40 pairs with double-precision
normalization and got:

```text
398 / 400 at 1e-6
```

Goal5228 showed the two failures pass at diagnostic `2e-6`, but Goal5229 tries
to avoid loosening tolerance by matching the author paper branch's float
coordinate normalization semantics.

## Review Questions

1. Does the author paper branch truly use `RunHausdorffDistanceImpl<float, 3>`
   for the default ModelNet40 path?
2. Is the new `normalize_point_matrix_to_author_float32_unit_box` helper
   correctly app-owned, with no X-HD/OFF/ModelNet40 semantics promoted to RTDL
   core?
3. Does the route gate record the new preprocessing as
   `normalize_each_input_to_author_float32_unit_box`?
4. Does the ModelNet40 batch runner forward `--author-float32-normalization`
   into the route gate?
5. Do the tests cover float32 normalization behavior and route metadata?
6. Does the all-400 float32-normalized run really report 400/400 matched at
   `1e-6`, with max diff `6.59728109919655e-08`?
7. Does this result correctly supersede the Goal5228 idea of loosening
   tolerance?
8. Does the report avoid claiming all-2000 completion, exact byte identity,
   fair performance ratio/parity, or full X-HD paper reproduction?

## Expected Verdict Label

```text
approve_goal5229_modelnet40_author_float32_normalization__all400_400_of_400_at_1e_minus_6
```
