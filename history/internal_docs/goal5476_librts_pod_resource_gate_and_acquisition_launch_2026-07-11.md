# Goal5476: LibRTS POD Resource Gate And Acquisition Launch

Date: 2026-07-11

## Result

The owner-provided POD passed the project SSH wrapper preflight:

```text
host = 157.157.221.29:24386
GPU = NVIDIA RTX 4000 Ada Generation
VRAM = 20,475 MiB
RAM = 473,009,446,912 bytes
/workspace free = 395,163,296,399,360 bytes
```

This exposed an overconstraint in Goal5474: archive acquisition/inventory does
not require 24 GiB GPU VRAM. The gate now separates:

```text
acquisition = Linux + >=70 GiB disk + >=64 GiB RAM
complete paper execution suitability = acquisition + >=24 GiB GPU VRAM
```

The POD plan therefore truthfully reports:

```text
status = resume_safe_acquisition_authorized
download_authorized = true
paper_execution_host_suitable = false
```

The 23.1 GB Zenodo download was launched through the Goal5474 `.part`/resume
runner under `/workspace/librts-data`. This report and committed plan do not
claim that the asynchronous transfer has completed. Completion, size+MD5
verification, inventory, and extraction are separate subsequent evidence.

## Parallel Build Staging

The official AE checkout and submodules were pinned on the POD:

```text
PPoPPAE = d605fe1bd5708cbf3c457a3a9698e0cc7bcdc14b
RTSpatial = 7c54c181b1058c87768767998c00e225cc58666e
RayJoin = 2151f56d09cbcfd4edbff259d97ac3123705411b
SpatialQueryBenchmark = 9140ad997519713bb5fdceba639a357afa4609ad
```

Pinned RTSpatial builds with CUDA 12.8 and the bundled OptiX 8 SDK. The
SpatialQueryBenchmark build is being staged separately while the archive
downloads; build completion is not claimed by this goal.

## Claim Boundary

Not claimed:

- completed download, verified archive, inventory, or extraction;
- complete paper-execution suitability on this 20 GiB GPU;
- paper figure reproduction or performance ratio;
- Embree evidence.

## Exit

```text
completed_pod_acquisition_resource_gate__download_launched_not_complete__review_pending
```
