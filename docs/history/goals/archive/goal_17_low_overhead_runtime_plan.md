# Goal 17: Low-Overhead Embree Runtime

Goal 17 is the first architecture-change milestone for RTDL's performance path.

The objective is not to replace the Python-like DSL.

The objective is to keep the DSL while reducing the current host/runtime overhead enough that RTDL moves materially closer to the pure native C++ + Embree path for the workloads already supported locally.

## Why This Goal Exists

Goal 15 showed that the current RTDL + Embree host path is significantly slower than the pure native wrapper:

- `lsi`: about `7.6x` slower than native
- `pip`: about `37.4x` slower than native

The main causes are:

- Python object materialization
- repeated normalization and validation
- `ctypes` marshaling
- Python-side result rematerialization

That means the current architecture uses Python as both:

- the DSL authoring layer
- and the execution data path

For the long-term v0.1 direction, that is not acceptable.

## Scope Of Goal 17

Goal 17 is a first low-overhead execution slice on top of Embree.

It does not attempt to solve all future backend-performance questions in one round.

Instead, it focuses on:

1. preserving the current Python-like DSL
2. reducing RTDL host-path overhead for the current Embree backend
3. proving a lower-overhead execution pattern for at least the currently compared workloads:
   - `lsi`
   - `pip`

## Required Deliverables

The first accepted slice should include:

1. A low-overhead runtime design note
   - explain the current hot-path overhead
   - explain the new execution contract

2. A prepared execution path
   - compile and validate the kernel once
   - bind native-ready inputs once
   - allow repeated execution without repeating the old normalization path

3. Native-ready packed input structures for at least:
   - segments
   - points
   - polygons

4. A public API that still keeps the Python DSL as the query surface
   - the user still writes RTDL kernels
   - the performance path changes underneath

5. Tests
   - correctness parity against the current RTDL paths
   - regression coverage for the new packed-input path
   - negative tests for invalid packed inputs

6. Benchmark evidence
   - compare:
     - current RTDL Embree path
     - new low-overhead RTDL path
     - Goal 15 pure native C++ + Embree path
   - for at least `lsi` and `pip`

## Acceptance Criteria

Goal 17 first slice is acceptable only if:

1. The Python-like DSL remains the user-facing query definition surface.
2. The new path is measurably faster than the old RTDL Embree path.
3. The new path preserves correctness parity.
4. The report clearly states how much of the native gap remains.
5. The wording is honest if the new path still does not fully match native.

## Non-Goals For This Round

This round does not require:

- a complete redesign of every workload path
- OptiX/NVIDIA work
- exact-performance parity with native C++ in one step
- removing Python completely from the control plane

The goal is a serious architecture shift, not a one-round miracle.

## Design Direction

The target direction is:

- Python DSL for authoring
- compiled execution plan for runtime
- flat native-ready packed buffers
- direct backend dispatch
- optional thin result views

In short:

- Python should remain the control plane
- Python should stop being the main data plane
