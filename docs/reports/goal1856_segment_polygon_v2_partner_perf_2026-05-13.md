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
to clean `origin/main` commit `bd8409b86d3ee45649d7411e2b6330c850acfc02`.

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
| v1.8 native OptiX rows | 0.0017824918 | 1.000x |
| v2.0 CuPy caller-supplied columns | 0.0010686070 | 0.600x |
| v2.0 Torch caller-supplied columns | 0.0011038482 | 0.619x |

The same harness was also run at 2048 rows:

| Path | Median query time (s) | Ratio vs v1.8 native query |
| --- | ---: | ---: |
| v1.8 native OptiX rows | 0.0075929612 | 1.000x |
| v2.0 CuPy caller-supplied columns | 0.0021268576 | 0.280x |
| v2.0 Torch caller-supplied columns | 0.0021966323 | 0.289x |

The first iteration includes one-time initialization effects and is retained in
the artifact rather than hidden. The median is the working comparison statistic
for this narrow row.

Column-build phase for the 512-row artifact:

- CuPy caller column build: 0.0042869225 s
- Torch caller column build: 0.0152883157 s

Column-build phase for the 2048-row artifact:

- CuPy caller column build: 0.0070429966 s
- Torch caller column build: 0.0183847174 s

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
