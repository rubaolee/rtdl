# Goal5238 X-HD Author PLY Loader Translation Contract Result

Date: 2026-07-09

## Verdict

`implemented__author_ply_loader_min_bound_translation_contract_confirmed__review_pending`

Goal5238 audits the author X-HD source code to explain why Goal5237 only
matches the author scaled-public all-source HDResult when RTDL applies
`translate_each_input_to_min_bound`.

Finding:

```text
For PLY inputs, the author loader independently translates each input point set
by subtracting that input's per-axis minimum coordinate.
```

Therefore the successful Goal5237 RTDL route is not an arbitrary route
normalization. It mirrors the author PLY loader's input contract.

## Author Source Evidence

Author source tree inspected on POD:

```text
/tmp/xhd-goal5112/author/src
```

### Input type dispatch

`main.cpp` maps `--input-type ply` to `InputType::kPLY`:

```cpp
} else if (input_type == "ply") {
  config.input_type = InputType::kPLY;
}
```

`run_hausdorff_distance.cu` dispatches PLY inputs to `LoadPLY` for both files:

```cpp
case InputType::kPLY: {
  points_a = LoadPLY<COORD_T, N_DIMS>(config.input_file1, config.limit);
  points_b = LoadPLY<COORD_T, N_DIMS>(config.input_file2, config.limit);
  break;
}
```

### PLY loader transform

`loaders/ply_loader.h` computes per-axis `vmin` / `vmax`, then applies:

```cpp
// move to 0,0
for (auto& v : vertices) {
  for (int i = 0; i < N_DIMS; ++i) {
    v[i] = (v[i] - vmin[i]);
  }
}
```

This transform is applied independently to each loaded PLY file because
`LoadPLY` is called separately for `points_a` and `points_b`.

### Distinction from optional normalize/translate flags

`run_hausdorff_distance.cu` also has optional post-load transforms:

```cpp
if (config.normalize) {
  NormalizePoints(points_a);
  NormalizePoints(points_b);
}
if (config.translate != 0) {
  TranslatePoints(points_b, 0, config.translate);
}
```

Goal5237 does not rely on these optional flags. The relevant behavior is the
unconditional `LoadPLY` min-bound subtraction for PLY input.

## RTDL App Contract

The RTDL X-HD app helper:

```python
translate_point_matrix_to_min_bound(matrix)
```

implements the same operation:

```python
coords -= coords.min(axis=0)
```

This is app-owned preprocessing that mirrors the author PLY loader. It is not a
generic RTDL coordinate transform, not a core primitive, and not an X-HD
algorithm shortcut.

## Relationship To Goal5237

Goal5237's three all-source runs now have a clear explanation:

```text
no translate:
  matched = false
  route distance = 0.1597462345977575
  reason = does not mirror author PLY loader min-bound translation

translate + global_bound_early_break:
  matched = false
  route distance = 0.06647010360490425
  reason = early-break mode is not exact for all-source HDResult

translate + no global_bound_early_break:
  matched = true
  route distance = 0.06536787240753439
  author_abs_diff = 2.3747470656587666e-09
  reason = mirrors author PLY loader preprocessing and uses exact-value mode
```

## Local Regression

Added:

```text
tests/goal5238_xhd_author_ply_loader_translation_contract_test.py
```

The test asserts:

1. RTDL app translation subtracts the per-axis minimum and leaves each axis
   minimum at zero.
2. This report documents `LoadPLY`, `v[i] = (v[i] - vmin[i])`,
   `app-owned preprocessing`, `RTDL core`, and `not a generic RTDL coordinate
   transform`.

## Validation

```text
py -m unittest tests.goal5238_xhd_author_ply_loader_translation_contract_test
Ran 2 tests OK
```

## Claim Boundary

Allowed:

```text
The independent min-bound translation used by the passing Goal5237 route
matches the author PLY loader's input preprocessing contract.
```

Not allowed:

```text
exact paper input byte identity is proved
Figure 6 is reproduced
author-vs-RTDL performance parity is proved
translation is a generic RTDL semantic requirement
global-bound early break is exact
full X-HD paper reproduction is complete
```

## Next Recommended Work

1. External review of Goals5233-5238 as one Dragon -> AsianDragon packet.
2. Fair performance matrix for the same scaled-public all-source input, with
   denominators separated:
   - author internal `AvgTime`
   - author process wall
   - RTDL route wall
   - RTDL full app wall
3. Continue to another paper workload family after the Dragon -> AsianDragon
   packet is reviewed.
