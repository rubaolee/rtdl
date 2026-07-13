# Goal5106 - RT-DBSCAN UCI 3DRoad Same-Source Candidate

Date: 2026-07-07

## Verdict

```text
uci_3droad_same_source_candidate_created__not_clean_exact_gate
```

Goal5106 followed the Goal5105 recommendation to pursue 3DRoad first. It
successfully pinned the public UCI source, generated author-format candidate
inputs, and ran a POD smoke against patched AuthorOfficial. The result is useful
but not a clean paper reproduction gate:

- UCI 3DRoad source is downloaded and SHA256-pinned.
- Deterministic author-format `(longitude, latitude, 0.0)` candidate inputs are
  generated for 1K, 16K, and full 434,874 rows.
- Patched AuthorOfficial produces a 1K payload and timing, but exits with
  `SIGSEGV` during devicegroup teardown.
- The 1K author payload and CPU reference agree on `core_count` and
  `core_flags`, but disagree on component signature / point partition.
- A 16K author run reaches timing output (`Total time = 92.4802s`) but also
  exits with `SIGSEGV`; it is therefore not a clean gate.
- RTDL OptiX+Numba partition route could not run on this POD because Numba
  emitted PTX 8.7 while the installed `ptxas` supports PTX 8.4.

This goal does not close exact RT-DBSCAN paper dataset reproduction.

## Source Pinning

Public source:

- [UCI 3D Road Network (North Jutland, Denmark)](https://archive.ics.uci.edu/dataset/246/3d+road+network+north+jutland+denmark)

Downloaded artifact:

```text
Paper-reproduction-apps/rt-dbscan-paper/data/source/uci_3droad/3d_road_network_north_jutland_denmark.zip
sha256=f68d145d85ea5df3e26bb0c218fe6789ab634786b7a67e16c0fc1a3efe5ac2a6
```

Extracted source:

```text
Paper-reproduction-apps/rt-dbscan-paper/data/source/uci_3droad/3D_spatial_network.txt
sha256=d83303a61dc3c9d0842df2c7e5b496ec29aafa2080a430253acb8411cae789dc
rows=434874
columns=OSM_ID,LONGITUDE,LATITUDE,ALTITUDE
```

The UCI page reports 434,874 instances and variables `OSM_ID`, `LONGITUDE`,
`LATITUDE`, and `ALTITUDE`. This matches the paper's approximate 435K 3DRoad
size, but it is still the public source, not the author's exact preprocessed
`3droad_full.csv`.

## Transform

New script:

```text
Paper-reproduction-apps/rt-dbscan-paper/scripts/prepare_uci_3droad_author_input.py
```

Default mode:

```text
paper_2d_zero_z
```

This writes:

```text
longitude,latitude,0.0
```

Rationale: the paper says 3DRoad is used as a 2D latitude/longitude dataset,
while the pinned author sample expects a three-float point stream.

Generated candidates:

```text
data/fixtures/uci_3droad_1k_author_2d_zero_z.csv
sha256=501407882ac0b4e02a9d81f235bce19371bb78a282bbb00299df0562916c2e0a

data/fixtures/uci_3droad_16k_author_2d_zero_z.csv
sha256=9f2d7678d463953fd9dda2a1e622a0d2be9c26194153a8ad6054bb34ff8f6120

data/fixtures/uci_3droad_full_author_2d_zero_z.csv
sha256=609cb1fba1268645f8b94c59fb4e250c151ad9573a7bd4dc5c088208d87ead84
```

Each summary is stored in `Paper-reproduction-apps/rt-dbscan-paper/results/`.

## POD Runs

POD:

```text
root@213.173.108.24 -p 13502
```

Author binary:

```text
/root/rtdl_goal5093/Paper-reproduction-apps/rt-dbscan-paper/_authorofficial_warm_work/build/sample02-rtdbscan
```

### 1K Author Direct Smoke

Command parameters:

```text
size=1000
epsilon=0.05
minPts=100
```

Author output:

```text
core_count=329
component_sizes=[90,168,181]
noise_count=561
cluster_formation_time_sec=0.605971
total_time_sec=1.1861
```

But the process exits with `SIGSEGV` during devicegroup teardown after writing
JSON/timing. Therefore this is not a clean AuthorOfficial gate.

### 1K CPU Reference Comparison

Artifact:

```text
Paper-reproduction-apps/rt-dbscan-paper/results/uci_3droad_1k_cpu_author_payload_compare_summary.json
```

Result:

```text
matched=false
signature_matched=false
component_partition_matched=false
core_flags_matched=true
author_signature={core_count=329, component_sizes=[90,168,181], noise_count=561}
cpu_signature={core_count=329, component_sizes=[102,168,181], noise_count=549}
```

Interpretation:

The fixed-radius core predicate agrees (`core_count` and `core_flags`), but
cluster/component assignment diverges. This means the UCI 3DRoad candidate
cannot be promoted to a component-partition correctness gate without further
contract analysis.

Possible causes include:

- author DBSCAN union/border assignment contract differs from the current CPU
  reference on larger/non-synthetic data;
- candidate preprocessing is not the author's paper preprocessing;
- numeric / ordering behavior differs from the bounded fixtures;
- the patched AuthorOfficial teardown crash indicates this route is not yet a
  stable author-comparator path.

### 16K Author Direct Smoke

Command parameters:

```text
size=16000
epsilon=0.05
minPts=100
```

The author stdout reaches:

```text
Execution time: 46.2203 seconds.
Total time = 92.4802
```

But it exits with `SIGSEGV` during teardown. This cannot be used as a clean
performance or correctness gate.

### RTDL OptiX+Numba Attempt

The RTDL OptiX+Numba component route failed before producing a result on this
POD:

```text
CUDA_ERROR_UNSUPPORTED_PTX_VERSION
ptxas application ptx input, line 9; fatal: Unsupported .version 8.7;
current version is '8.4'
```

This is an environment/toolchain blocker for that POD run, not a data
correctness result.

## What This Proves

Proved:

- UCI 3DRoad public source can be pinned and transformed into the author input
  shape.
- The pinned author binary can ingest at least the 1K same-source candidate and
  produce DBSCAN payload/timing before teardown.
- The 1K candidate exposes a real contract mismatch beyond core-count.

Not proved:

- exact paper input provenance;
- exact paper dataset reproduction;
- clean AuthorOfficial gate on 3DRoad;
- RTDL OptiX+Numba partition correctness on 3DRoad;
- paper-performance reproduction;
- author-performance parity.

## Authorized Claim

Allowed:

```text
Goal5106 created a pinned UCI 3DRoad same-source candidate and found that it is
not yet a clean exact-paper or component-partition correctness gate. The first
1K smoke matches AuthorOfficial on core flags but diverges on component
partition/signature; 16K and 1K author runs also expose a teardown SIGSEGV.
```

Forbidden:

```text
exact 3DRoad paper input reproduced
RT-DBSCAN paper dataset reproduced
RTDL matches AuthorOfficial on 3DRoad components
RTDL performance on 3DRoad paper workload
```

## Recommended Next Goal

Goal5107 should not jump to full 3DRoad timing. It should first do one of:

1. **Contract-debug route:** construct a minimal UCI-derived witness for the
   1K author-vs-CPU component mismatch and determine whether the difference is
   author contract, preprocessing, or a CPU reference assumption.
2. **Author-stability route:** patch AuthorOfficial teardown so same-source
   runs exit cleanly after emitting JSON, without changing kernel semantics.
3. **Environment route:** fix the POD Numba/PTX version mismatch, then rerun
   RTDL OptiX+Numba on the 1K same-source candidate.

The safest next move is route 1 plus route 2: reduce the mismatch and make the
author comparator clean before scaling.
