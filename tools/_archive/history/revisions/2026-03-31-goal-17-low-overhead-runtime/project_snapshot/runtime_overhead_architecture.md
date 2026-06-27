# RTDL Runtime Overhead Architecture

This document explains the current end-to-end execution shape of RTDL on Embree, why it is slower than the pure native C++ + Embree path, and what architecture change is required if RTDL is expected to stay close to low-level backend performance.

## Current Comparison Boundary

Goal 15 compared:

- RTDL + Embree
- pure C++ + Embree

for the same deterministic `lsi` and `pip` fixtures.

The important result was:

- correctness matched on the tested cases
- native was materially faster
- the difference was mainly host-path overhead, not a different Embree traversal core

Measured examples from Goal 15:

- `lsi`
  - native: `0.004039875 s`
  - RTDL Embree: `0.030882917 s`
  - slowdown: about `7.6x`
- `pip`
  - native: `0.000565042 s`
  - RTDL Embree: `0.021154667 s`
  - slowdown: about `37.4x`

## Current RTDL End-to-End Path

For a workload such as `lsi`, the current RTDL path is:

1. author the query in the Python DSL
2. create Python-side geometry objects
3. compile and validate the RTDL kernel
4. normalize Python records into RTDL logical records
5. marshal those records into `ctypes` native structs
6. call the native Embree entry point
7. rematerialize native rows into Python dictionaries

Conceptually:

```text
Python DSL
  -> RTDL compile / validate / lower
  -> Python input normalization
  -> ctypes marshaling
  -> native Embree backend
  -> native rows
  -> Python dict rows
```

## Current Pure Native Path

The pure C++ + Embree comparison path is thinner:

1. parse or construct native input arrays
2. call the native Embree entry point directly
3. collect native rows
4. serialize output

Conceptually:

```text
C++ app
  -> native input arrays
  -> native Embree backend
  -> native rows
  -> output serialization
```

## Where The Current Overhead Comes From

The main costs in RTDL today are:

- Python object creation for segments, points, polygons, rays, and triangles
- repeated kernel/input validation during execution
- normalization of user inputs into RTDL reference dataclasses
- `ctypes` marshaling into native buffers
- Python-side result rematerialization into dictionaries

This means the current architecture treats Python as both:

- the authoring layer
- and the execution data path

That is convenient for prototyping, but it is the wrong shape if RTDL is expected to preserve backend-level performance.

## What Must Change

The Python-like DSL can stay.

The hot execution path should change.

The target architecture is:

1. Python-like DSL for authoring
2. compile once into a stable execution plan
3. bind flat, native-ready buffers at runtime
4. dispatch the backend directly
5. expose thin result views, with optional Python materialization only when needed

Conceptually:

```text
Python-like DSL
  -> compiled execution plan
  -> flat buffers / packed arrays
  -> direct native backend dispatch
  -> native result buffers
  -> optional thin Python view
```

## Design Rule

If RTDL is meant to remain competitive with no-DSL low-level implementations, then:

- Python should remain the control plane
- Python should not remain the main data plane

That is the central architecture conclusion from the current Embree comparison work.

## Goal 17 First Result

Goal 17 implemented the first low-overhead Embree runtime slice for:

- `lsi`
- `pip`

The measured result was:

- packed inputs alone were not enough to improve the ordinary dict-return `lsi` path
- packed inputs plus a thin native result view did materially reduce the gap

That means the redesign direction is now supported by measured repo evidence rather than only architectural argument.
