# Goal5454 - LibRTS Same-Input Point-Contains Gate

Date: 2026-07-10

## Objective

Run the pinned author RTSpatial/OptiX example and the public RTDL OptiX API on
the same deterministic tiny box/point files. Close only the bounded result-count
contract that the unmodified author example exposes.

## Environment

```text
host = lx1 / 192.168.1.20
GPU = NVIDIA GeForce GTX 1070
driver = 580.126.09
CUDA = 12.0
OptiX SDK = /home/lestat/vendor/optix-dev
evidence class = functional Linux evidence only
performance evidence authorized = false
Embree used = false
```

## Author Provenance And Build

The gate verifies the checkout with `git rev-parse HEAD` before execution:

```text
expected = 52509e8022abeab722f5a9a89d1917e8b481defe
observed = 52509e8022abeab722f5a9a89d1917e8b481defe
match = true
```

The local Linux build needed compatibility-only adaptations:

- author CUDA architecture `75 -> 61` for GTX 1070;
- user-prefix gflags 2.2.2;
- discoverable system Boost serialization runtime;
- GCC/G++ 12 and CUDA-12/GCC intrinsic-header guards.

The arch patch and build notes are committed under
`Paper-reproduction-apps/librts-paper/author_patches/`. None changes author
query semantics, result collection, or timing code.

RTDL `build/librtdl_optix.so` was independently rebuilt from the current source
in the isolated Linux staging directory. No Embree target was built or run.

## Same Input Identity

Both implementations received the same files:

```text
tiny_boxes.wkt  sha256 = 12629026e7323d795d00407a3ac7b11206eca18b442ac8357b2870e57922e3f2
tiny_points.wkt sha256 = 70f90a6ed38b627f498bd62d1d94355ce8476190228f4d5ba84a79b5a96537a4
expected JSON   sha256 = dfe6beadd8e8d87d99acac8363cf7088e8f5e4072cb2ff06ac53221b8d758e5a
```

## Result

```text
author RTSpatial/OptiX result count = 5
RTDL OptiX result count             = 5
RTDL rt_core_accelerated            = true
RTDL native_engine_customization    = false
matched                              = true
```

RTDL also emits the exact deterministic relation:

```text
(query_id, box_id) =
(0,0), (1,0), (1,1), (2,1), (3,2)
```

The author example prints only the total count. It does not expose pair rows.
Therefore this goal proves author/RTDL same-input result-count agreement and
RTDL exact-row agreement with the fixture. It does **not** prove author/RTDL
pair-relation equality.

Committed evidence:

```text
Paper-reproduction-apps/librts-paper/results/librts_goal5454_same_input_point_contains.json
```

## Timing Boundary

The artifact records one author diagnostic (`load 2.445ms`, `query 0.081ms`).
No RTDL timing was collected under a matched phase boundary, and the GTX 1070
is not paper-performance hardware. No speedup, parity, or performance ratio is
authorized.

## Validation

```text
Windows focused LibRTS/portfolio tests: 21 OK
Linux Goal5453 + Goal5454 tests: 10 OK
Linux author build: pass
Linux RTDL OptiX build: pass
Linux same-input author/RTDL gate: matched
```

The first Linux staging attempt omitted the portfolio snapshot and failed one
test on missing file; after the snapshot was added, the complete staged test
passed. A later JSON-display one-liner had a shell quoting error; the already
written result was read directly and was valid. Neither issue is represented as
an algorithm or backend failure.

## Claim Boundary

Authorized:

- one bounded same-input point-contains result-count agreement;
- RTDL exact-row agreement with the deterministic fixture;
- pinned-author and public-RTDL OptiX functional execution on local Linux.

Not authorized:

- author pair-row equality;
- range-contains or range-intersects reproduction;
- mutable Insert/Update/Delete/Clear parity;
- Ray Multicast or PIP equivalence;
- paper datasets, figures, or full reproduction;
- any performance comparison;
- Embree evidence;
- a LibRTS-specific RTDL core primitive.

## Next Goal

Goal5455 should add a discriminating range-contains fixture and run author
RTSpatial/OptiX and RTDL OptiX on the same files. It must preserve the same
count-vs-row distinction if the author example still exposes count only.

## Exit Label

```text
goal5454_librts_same_input_point_contains_count_matched__review_pending
```
