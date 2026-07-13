# Call For Review: Goal5219 ModelNet40 Normalized OFF Contract Probe

Date: 2026-07-09

Please strictly review Goal5219.

Primary report:

```text
history/internal_docs/goal5219_modelnet40_normalized_off_contract_probe_result_2026-07-09.md
```

Evidence artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5219_modelnet40_glass_box_author_normalized_probe_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5219_modelnet40_glass_box_rtdl_normalized_route_summary_2026-07-09.json
```

Implementation changes:

```text
Paper-reproduction-apps/x-hd-paper/scripts/xhd_input_loader.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
tests/goal5219_xhd_off_normalize_input_contract_test.py
```

## Context

Goal5218 proved that official public ModelNet40 raw OFF files are
count-compatible with one author paper-branch pair, but raw coordinates do not
match the paper log:

```text
paper-branch HDResult           = 0.22594279050827026
author hd_exec on public raw OFF = 1115.2059326171875
```

The author paper log for the pair records `Input.Normalize=true`. Goal5219
tests the author normalize contract and then runs the RTDL route on the same
normalized public OFF input.

## Key Evidence

Selected pair:

```text
ModelNet40/glass_box/train/glass_box_0115.off
ModelNet40/glass_box/train/glass_box_0081.off
point counts = [1107, 1200]
paper-branch HDResult = 0.22594279050827026
paper-branch Normalize = true
```

Author source contract:

```text
-normalize (Normalize points to [0, 1]) type: bool default: false

NormalizePoints(points):
  subtract per-axis lower bound
  divide by max axis extent for that input
```

Author binary on public raw OFF with `-normalize=true`:

```text
HDResult = 0.22594279050827026
Input.Normalize = true
Input.Type = Float
Input.Translate = 0.0
Input counts = [1107, 1200]
```

This equals the paper-branch log HDResult exactly for this pair. The normalized
MBRs also match the logged MBRs:

```text
file1 x[0,0.5865572094917297], y[0,1], z[0,0.27818214893341064]
file2 x[0,0.8333333134651184], y[0,1], z[0,0.3683861196041107]
```

RTDL route on app-owned normalized OFF input:

```text
RTDL route directed_a_to_b = 0.22594284338858983
RTDL exact reference       = 0.22594284338858983
author normalized HDResult = 0.22594279050827026
RTDL exact abs diff        = 0.0
RTDL vs author abs diff    = 5.288031956762751e-08
matched                    = true
tolerance                  = 1e-6
```

Local tests:

```text
py -m unittest tests.goal5219_xhd_off_normalize_input_contract_test
Ran 4 tests OK

py -m unittest tests.goal5203_numpy_point_matrix_input_loader_test \
  tests.goal5205_fast_ascii_ply_matrix_loader_test \
  tests.goal5133_xhd_ply_input_bridge_test
Ran 14 tests OK
```

## Requested Verdict Labels

Choose one:

```text
approve_goal5219_modelnet40_normalized_contract_one_pair_reconstructed
approve_with_required_amendments
revise_goal5219_before_using_modelnet40_batch
block_due_to_invalid_normalize_contract_or_overclaim
```

## Review Questions

1. Does the author source/CLI evidence establish that `-normalize=true` is an
   official author preprocessing contract?

2. Does the author normalized run exactly reproduce the selected paper-branch
   ModelNet40 HDResult and logged MBRs for this one pair?

3. Is it correct to interpret Goal5218 + Goal5219 as:

   ```text
   public raw OFF alone does not match;
   public raw OFF plus author NormalizePoints matches this pair.
   ```

4. Does the RTDL app-owned OFF+normalize route correctly avoid adding OFF or
   X-HD normalize semantics to RTDL core?

5. Does the RTDL route evidence support only a bounded one-pair correctness
   claim under float-author tolerance, not a performance or algorithm-parity
   claim?

6. Is the `1e-6` tolerance appropriate for comparing RTDL float64 normalized
   route output against author `Input.Type=Float` output?

7. Does the report avoid claiming full ModelNet40 reproduction, exact paper
   dataset identity, author performance parity, or all-pair reproduction?

8. Is the next recommendation correct: batch-test the same normalized
   author+RTDL gate across multiple ModelNet40 paper-branch pairs before
   promoting ModelNet40 to a stronger Level-C candidate?

## Expected Answer Shape

```text
Verdict:
<one requested verdict label>

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers:
1. ...
...
8. ...
```

## Non-Authorization Boundary

This review must not authorize:

```text
full X-HD paper reproduction;
ModelNet40 full reproduction complete;
public raw OFF equals paper input without preprocessing;
all ModelNet40 pairs reproduce;
exact paper dataset identity proved;
author performance parity;
author-vs-RTDL ratio;
X-HD fused RT-core algorithm fully reproduced.
```
