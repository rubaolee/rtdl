# Goal5125 - X-HD Bounded Same-Input Closeout Packet

Date: 2026-07-08

## Verdict

```text
xhd_bounded_same_input_reproduction_complete
```

## Scope Closed

This closes the X-HD paper app line as a bounded same-input reproduction
candidate, pending consolidated external review.

Closed evidence:

- author source provenance pinned;
- author `hd_exec` built and run on POD as `Author+BuildPatch`;
- tiny2d, bounded2d, and bounded3d author JSON gates matched;
- directed-asymmetric 2D gate matched and distinguishes author directed
  input1-to-input2 from symmetric Hausdorff max;
- bounded2d and bounded3d paper app routes use RTDL public columnar APIs and
  match author `HDResult`;
- author `HDResult` comparator is explicitly directed input1-to-input2;
- phase/performance matrix separates author internal `Running.AvgTime`, author
  process wall, and RTDL local route phases;
- system API extraction identifies generic RTDL additions vs app-owned code.

## Not Closed

Not closed and not claimed:

- full X-HD paper reproduction;
- exact paper dataset reproduction;
- representative same-source reproduction;
- author X-HD RT-core algorithm equivalence;
- author performance parity;
- whole-program or phase speedup.

## Result Inventory

```text
Paper-reproduction-apps/x-hd-paper/results/tiny2d_author_gate_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/bounded2d_author_gate_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/bounded3d_author_gate_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/bounded2d_rtdl_route_gate_summary.json
Paper-reproduction-apps/x-hd-paper/results/bounded3d_rtdl_route_gate_summary.json
Paper-reproduction-apps/x-hd-paper/results/xhd_bounded_performance_matrix_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_author_build_patch_goal5112.diff
```

## Key Numbers

Correctness:

| Fixture | Dimensions | Author HDResult | RTDL / exact directed A->B | Matched |
| --- | ---: | ---: | ---: | --- |
| tiny2d | 2 | 1.0 | 1.0 | yes |
| directed2d_asymmetric | 2 | 0.5 | 0.5 | yes |
| bounded2d | 2 | 2.0 | 2.0 | yes |
| bounded3d | 3 | 2.0 | 2.0 | yes |

The directed-asymmetric fixture has `directed_b_to_a=9.0` and
`symmetric_hausdorff_diagnostic=9.0`, so it would fail if the author comparator
used the symmetric max instead of directed input1-to-input2.

Phase disclosure:

| Fixture | Author retained Running.AvgTime | Author wall median | RTDL local route phase |
| --- | ---: | ---: | ---: |
| bounded2d | 3.873 ms | 1.079 s | 1.42 ms |
| bounded3d | 4.235 ms | 1.104 s | 1.59 ms |

No speedup ratio is reported.

## System / App Boundary

System additions:

```text
point_rows_to_numpy_columns_3d
directed_hausdorff_3d_numpy_columns
```

System assets reused:

```text
point_rows_to_numpy_columns
directed_hausdorff_2d_numpy_columns
prepare_generic_fixed_radius_count_threshold_2d
```

App-owned:

```text
author build/run wrapper
author JSON comparator
fixture/data policy
tolerance policy
performance matrix wording
```

## Review Status

Goal5110 was externally reviewed and approved. Goals5111-5125 were sent as a
consolidated review packet. Goal5126 was added as the directed-semantics
amendment and externally verified. The bounded same-input line is now approved.

## Closeout Label

```text
xhd_bounded_same_input_reproduction_complete
```
