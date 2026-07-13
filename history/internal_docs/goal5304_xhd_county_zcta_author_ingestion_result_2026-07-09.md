# Goal5304 X-HD County-ZCTA Author Ingestion Result

Date: 2026-07-09

## Verdict

`completed_county_zcta_author_ingestion__author_hd_exec_passed__rtdl_not_run`

## Purpose

Goal5304 runs the author X-HD `hd_exec` binary on the Goal5303 bounded
County-ZCTA WKT fixture.

This is an author-ingestion gate only. It proves that the generated WKT files
can be read by the author program and produce an author JSON summary. It does
not run RTDL, does not claim author/RTDL correctness, and does not claim
performance.

## POD / Author Environment

POD access used only the project wrapper:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
```

Preflight:

```text
POD_OK
hostname = 45c502cfccb5
gpu = NVIDIA RTX 4000 Ada Generation
driver = 550.127.05
```

Author binary:

```text
/tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec
```

Remote fixture directory:

```text
/tmp/xhd_goal5304/data
```

Remote hash check:

```text
204551e901d3695cffcf0701993e037dcd805494d0e6518c3ec6e3f01f7526aa  dtl_cnty_arcgis_bounded.wkt
5cc9ee7fee44348f1ba1110d1e6e07bb490b762df1c5e5e5a3e55b8cf9903e91  uszipcode_arcgis_bounded.wkt
```

## Author Command

```text
/tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec \
  -input1 /tmp/xhd_goal5304/data/dtl_cnty_arcgis_bounded.wkt \
  -input2 /tmp/xhd_goal5304/data/uszipcode_arcgis_bounded.wkt \
  -input_type wkt \
  -n_dims 2 \
  -variant rt \
  -execution gpu \
  -json /tmp/xhd_goal5304/out/author_county_zcta_arcgis_bounded.json \
  -overwrite=true \
  -check=false \
  -normalize=false
```

Downloaded raw outputs:

```text
Paper-reproduction-apps/x-hd-paper/results/goal5304_raw/author_county_zcta_arcgis_bounded.json
Paper-reproduction-apps/x-hd-paper/results/goal5304_raw/author_stdout.txt
Paper-reproduction-apps/x-hd-paper/results/goal5304_raw/author_stderr.txt
```

Summary artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5304_county_zcta_author_ingestion_summary_pod.json
```

## Result

Author `hd_exec` succeeded and produced JSON.

Key fields:

```text
HDResult = 65.44752502441406
Input.NumDims = 2
Input.Normalize = false
Input.Files[0].NumPoints = 38034
Input.Files[1].NumPoints = 50272
Running.AvgTime = 6.169 ms
Running.Repeats[0].ReportedTime = 6.169 ms
GridResolution = [12, 8]
LargeCells = 40
Iterations = 2
```

stderr confirms the same author-loader point counts:

```text
Points A: 38034 Points B: 50272
HausdorffDistance: distance is 65.4475
```

These point counts match the Goal5303 manifest's author-loader outer-ring point
estimates:

```text
county estimate = 38034
zipcode estimate = 50272
```

## Interpretation

This closes the first author-side executable gate for the non-graphics geo
path:

```text
Goal5303 WKT fixture -> author hd_exec JSON
```

It proves the bounded ArcGIS WKT fixture is readable by the author binary under
the expected paper geo flags:

```text
input_type = wkt
n_dims = 2
normalize = false
variant = rt
execution = gpu
```

It does not prove:

```text
RTDL route correctness;
author/RTDL agreement;
exact paper dataset identity;
geo Figure 5 reproduction;
performance ratio;
full paper reproduction.
```

Important fixture caveat from Goal5303 still applies:

```text
The first County OBJECTIDs are Alabama counties, while the first ZIP/ZCTA
OBJECTIDs are Alaska ZCTAs. This is an ingestion/conversion gate, not
geographic representativeness evidence.
```

## Claim Boundary

Allowed summary:

```text
Goal5304 proves that the Goal5303 bounded ArcGIS County-ZCTA WKT fixture can be
ingested by the author `hd_exec` binary and produces an author JSON with
HDResult=65.44752502441406 and point counts 38034/50272.
```

Forbidden summaries:

```text
RTDL matches author on County-ZCTA.
Geo Figure 5 is reproduced.
Exact X-HD geo paper input is recovered.
The ArcGIS fixture is geographically representative.
Author-vs-RTDL performance can now be compared.
Full X-HD paper reproduction is complete.
```

## Validation

Commands run locally:

```text
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5304_county_zcta_author_ingestion_summary_pod.json
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/goal5304_raw/author_county_zcta_arcgis_bounded.json
py -m unittest tests.goal5304_xhd_county_zcta_author_ingestion_test
```

Test result:

```text
Ran 3 tests in 0.001s
OK
```

## Next Recommended Goal

Goal5305 should run the RTDL route on the same bounded WKT fixture only after
accepting this author-ingestion result.

Scope for Goal5305:

```text
1. Use the same local WKT files and the same author-result JSON.
2. Run RTDL with the directed input1->input2 contract.
3. Compare RTDL HDResult to the Goal5304 author HDResult under an explicit
   tolerance.
4. Keep this as Level-B bounded geo correctness only.
5. Do not report author-vs-RTDL performance ratio unless denominator review is
   separately authorized.
```
