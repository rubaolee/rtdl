# Goal1678 Python RTDL Pod Embree Build

Date: 2026-05-10

Status: pod evidence for the Python+RTDL v1.8 track.

## Verdict

The staged pod tree can build and load the Embree backend after installing the
missing system development packages:

```text
apt-get install -y libembree-dev libgeos-dev
```

Validation command:

```text
cd /tmp/rtdl_goal167x_validate
make build-embree
```

Result:

```text
Embree 3.12.2
```

This moves the pod from "Embree dependency missing" to "Embree backend build
and load smoke passes" for the current source tree.

## Boundary

This is a build/load smoke, not a complete v1.8 release authorization. The
native app-agnostic gate still fails until remaining database, graph,
polygon/GIS, KNN, Hausdorff, and Jaccard native surfaces are migrated or
quarantined.

OptiX remains blocked on this pod because the NVIDIA OptiX SDK headers are not
installed:

```text
/opt/optix/include/optix.h
```

`nvcc` is available at `/usr/local/cuda-12.4/bin/nvcc`, so the missing item for
the OptiX build target is the SDK header package, not CUDA itself.
