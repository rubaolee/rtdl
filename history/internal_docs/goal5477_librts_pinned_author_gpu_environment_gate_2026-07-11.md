# Goal5477: LibRTS Pinned Author GPU Environment Gate

Date: 2026-07-11

## Result

The pinned official AE and all three submodules were checked out on the owner
POD. RTSpatial, SpatialQueryBenchmark `query`, and `pip` were built without
modifying author algorithm source.

Pinned commits:

```text
PPoPPAE = d605fe1bd5708cbf3c457a3a9698e0cc7bcdc14b
RTSpatial = 7c54c181b1058c87768767998c00e225cc58666e
RayJoin = 2151f56d09cbcfd4edbff259d97ac3123705411b
SpatialQueryBenchmark = 9140ad997519713bb5fdceba639a357afa4609ad
```

Environment:

```text
GPU = NVIDIA RTX 4000 Ada Generation, 20,475 MiB, driver 580.65.06
CUDA = 12.8
OptiX = bundled author SDK 8.0
CMake = 3.28.3
benchmark host compiler = GCC/G++ 12
GEOS = author-pinned 3.11.0 under private AE prefix
Embree = not used
```

Ubuntu 24 supplies GEOS 3.12 with an incompatible C++ header surface. The AE's
pinned GEOS 3.11 was built under GCC12 to preserve author dependency source;
no GLIN/query/PIP algorithm source was patched.

## Hardware Smoke

The standard author binaries were run on the existing bounded fixtures:

```text
query point-contains result count = 5 (expected 5)
pip result count = 4 (expected 4)
```

Both match the previously closed author/RTDL bounded gates. This proves the
pinned author GPU executables and compute-75 PTX load/run on RTX 4000 Ada.

Machine evidence:

```text
Paper-reproduction-apps/librts-paper/results/librts_goal5477_author_pod_environment.json
```

Focused tests: 3 OK.

## Boundary

Authorized: the author GPU environment is ready for exact-input gates that fit
this POD. Not authorized: completed archive download, exact input identity,
complete 24 GiB paper matrix capacity, figure reproduction, performance ratio,
or Embree evidence.

## Exit

```text
completed_pinned_author_gpu_environment_gate__exact_archive_pending__review_pending
```
