# Goal5311 - X-HD WaterBodies -> BlockGroups Full-Public Author Ingestion Result

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

Goal5311 runs the author X-HD `hd_exec` binary on the Goal5310 full-public
WaterBodies -> BlockGroups WKT candidate.

This is an author-ingestion gate only. It proves the full-public generated WKT
files are readable by the author program and produce an author JSON. It also
shows that this full-public candidate is **not** a paper-log value match.

## Artifacts

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5311_water_bg_full_public_author_ingestion_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/goal5311_raw/author_water_bg_full_public.json
Paper-reproduction-apps/x-hd-paper/results/goal5311_raw/author_stdout.txt
Paper-reproduction-apps/x-hd-paper/results/goal5311_raw/author_stderr.txt
tests/goal5311_xhd_water_bg_full_public_author_ingestion_test.py
```

Input candidate from Goal5310:

```text
WaterBodies WKT sha256 =
  0c4ad7d7c1953364478d4940a8eb1696cca24d0dfd6422aafc532b1983f3dd39

BlockGroups WKT sha256 =
  8a1d3cd848083e5182de81521f07d8850c597910320250066d850928b017e66e
```

## POD / Author Environment

POD wrapper preflight:

```text
POD_OK
hostname = 45c502cfccb5
GPU = NVIDIA RTX 4000 Ada Generation
driver = 550.127.05
```

Author binary:

```text
/tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec
```

Remote input directory:

```text
/tmp/xhd_goal5311/data
```

Remote WKT hash verification:

```text
8a1d3cd848083e5182de81521f07d8850c597910320250066d850928b017e66e  USACensusBlockGroupBoundaries.wkt.full_public_arcgis_candidate.wkt
0c4ad7d7c1953364478d4940a8eb1696cca24d0dfd6422aafc532b1983f3dd39  USADetailedWaterBodies.wkt.full_public_arcgis_candidate.wkt
```

## Author Command

```text
/tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec \
  -input1 /tmp/xhd_goal5311/data/USADetailedWaterBodies.wkt.full_public_arcgis_candidate.wkt \
  -input2 /tmp/xhd_goal5311/data/USACensusBlockGroupBoundaries.wkt.full_public_arcgis_candidate.wkt \
  -input_type wkt \
  -n_dims 2 \
  -variant rt \
  -execution gpu \
  -json /tmp/xhd_goal5311/out/author_water_bg_full_public.json \
  -overwrite=true \
  -check=false \
  -normalize=false
```

## Result

Author `hd_exec` succeeded.

```text
HDResult = 0.8970130085945129
paper-log HDResult = 0.8964367508888245
abs delta vs paper log = 0.0005762577056884766
paper value matched = false
```

Input counts:

```text
Points A = 22,824,823
Points B = 52,271,467
```

These exactly match the Goal5310 full-public WKT manifest:

```text
Goal5310 WaterBodies points = 22,824,823
Goal5310 BlockGroups points = 52,271,467
```

Author timing fields:

```text
Running.AvgTime = 103.564 ms
ReportedTime = 103.564 ms
GridResolution = [2304, 1078]
LargeCells = 61,275
Iterations = 12
```

The author stderr confirms the same point counts and result:

```text
Points A: 22824823 Points B: 52271467
Avg Running Time 103.564 ms
HausdorffDistance: distance is 0.897013
```

## Interpretation

Goal5311 closes this executable chain:

```text
Goal5309 point-count/MBR probe
  -> Goal5310 full-public Water/BG WKT materialization
  -> Goal5311 author hd_exec JSON
```

But it also blocks the stronger Figure-5 claim for this candidate:

```text
The public ArcGIS WaterBodies-BG candidate is author-executable and close in
count/MBR, but it does not reproduce the paper-log HDResult.
```

This is now a Level-B full-public author-ingestion result, not exact paper
dataset reproduction.

## Claim Boundary

Allowed summary:

```text
Goal5311 proves that the Goal5310 full-public WaterBodies-BlockGroups WKT
candidate can be ingested by author hd_exec. The author result is
HDResult=0.8970130085945129, with point counts 22,824,823 / 52,271,467.
```

Forbidden summaries:

```text
WaterBodies-BlockGroups Figure 5 is reproduced.
The full-public ArcGIS candidate matches the paper log.
Exact paper WKT inputs are recovered.
RTDL matches author on this full-public candidate.
Author-vs-RTDL performance ratio is available.
Full X-HD paper reproduction is complete.
```

## Validation

Commands run:

```text
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5311_water_bg_full_public_author_ingestion_summary_pod.json
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/goal5311_raw/author_water_bg_full_public.json
py -m unittest tests.goal5311_xhd_water_bg_full_public_author_ingestion_test tests.goal5310_xhd_water_bg_full_public_wkt_candidate_test
```

Results:

```text
JSON validation OK
Ran 10 tests OK
```

## Next Recommended Goal

If continuing this full-public candidate line, the next goal should run RTDL on
the same WaterBodies-BlockGroups candidate and compare against the Goal5311
author HDResult only as a **Level-B full-public author/RTDL scalar comparison**.

It must keep these boundaries:

```text
paper-log mismatch visible;
no exact paper input claim;
no Figure-5 reproduction claim;
no performance ratio unless a separate denominator review approves one.
```
