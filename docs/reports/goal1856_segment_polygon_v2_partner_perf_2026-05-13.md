# Goal1856 - First v2.0 Partner vs v1.8 Same-Contract Timing Row

Status: pass-with-boundary

Date: 2026-05-13

## Scope

Goal1856 adds a narrow timing harness for the first app-level v2.0 partner row:

`scripts/goal1856_segment_polygon_v2_partner_perf.py`

The measured app is `segment_polygon_anyhit_rows`. The comparison is:

- v1.8/current native OptiX row path:
  `segment_polygon_anyhit_rows_native_bounded_optix`
- v2.0 preview caller-supplied partner-column path:
  `segment_polygon_anyhit_rows_optix_partner_columns`

Both paths emit the same `segment_id` / `polygon_id` row contract. Parity is
checked as a canonical row set because native traversal order is not a public
semantic.

## Pod Evidence

The harness was run on the available RTX A4500 pod after resetting `/root/rtdl`
to clean `origin/main` commit `cb1937db4f...` and rebuilding
`build/librtdl_optix.so` with the corrected all-witness launch parameter
layout.

Command shape:

```text
PYTHONPATH=src:. LD_LIBRARY_PATH=/root/rtdl/build:$LD_LIBRARY_PATH \
python3 scripts/goal1856_segment_polygon_v2_partner_perf.py \
  --count 512 \
  --iterations 5 \
  --partners cupy,torch \
  --output docs/reports/goal1856_segment_polygon_v2_partner_perf_pod_512.json
```

Artifacts:

`docs/reports/goal1856_segment_polygon_v2_partner_perf_pod_512.json`

`docs/reports/goal1856_segment_polygon_v2_partner_perf_pod_2048.json`

## Observed Timing

Dataset: 512 synthetic segment/triangle rows, 512 expected output rows,
bounded output capacity 1024.

| Path | Median query time (s) | Ratio vs v1.8 native query |
| --- | ---: | ---: |
| v1.8 native OptiX rows | 0.0019464493 | 1.000x |
| v2.0 CuPy caller-supplied columns | 0.0011272132 | 0.579x |
| v2.0 Torch caller-supplied columns | 0.0010540113 | 0.542x |

The same harness was also run at 2048 rows:

| Path | Median query time (s) | Ratio vs v1.8 native query |
| --- | ---: | ---: |
| v1.8 native OptiX rows | 0.0075653195 | 1.000x |
| v2.0 CuPy caller-supplied columns | 0.0021255687 | 0.281x |
| v2.0 Torch caller-supplied columns | 0.0021432191 | 0.283x |

The first iteration includes one-time initialization effects and is retained in
the artifact rather than hidden. The median is the working comparison statistic
for this narrow row.

Column-build phase for the 512-row artifact:

- CuPy caller column build: 0.0042869225 s
- Torch caller column build: 0.0157439113 s

Column-build phase for the 2048-row artifact:

- CuPy caller column build: 0.0070429966 s
- Torch caller column build: 0.0184309483 s

Overflow checks are now part of both artifacts:

- 512-row artifact: CuPy and Torch both fail closed at tight capacity 256.
- 2048-row artifact: CuPy and Torch both fail closed at tight capacity 1024.

Those build timings are reported separately because the Goal1853 adapter target
is caller-supplied GPU columns: in the intended v2.0 shape, a learner or partner
pipeline may already own the tensors before calling RTDL.

## Boundary

This is the first same-contract v2.0-vs-v1.8 timing row for one app path. It is
not an all-app performance table and does not authorize v2.0 release wording.

No whole-app speedup claim, broad RT-core speedup claim, package-install claim,
or v2.0 release claim is authorized by this goal.

The result is useful engineering evidence: the caller-supplied partner-column
shape can preserve row semantics and reduce the median measured query phase for
this small synthetic row on the RTX A4500. It must be scaled, reviewed, and
repeated across the remaining app surface before any public release conclusion.

## External Review

Claude reviewed Goal1856 in
`docs/reviews/goal1857_claude_review_goal1856_v2_partner_perf_row_2026-05-13.md`
with verdict `accept-with-boundary`.

The review accepts this as an internal engineering data point and keeps all
public/release claims blocked. The highest-priority follow-up gaps are:

- column-build amortization/accounting,
- broader scale sweep,
- overlapping/multi-hit geometry parity,
- overflow-boundary testing,
- additional GPU-class evidence.
