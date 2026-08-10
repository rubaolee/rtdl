# RTDL 3.0.0 Release Notes

RTDL 3.0.0 is the first V3 source release. It promotes the project from
app-directed physical routing to compiler-owned, canonical semantic lowering
for the supported NVIDIA OptiX universe.

## Highlights

- A finite, typed Action language for bounded non-graphical RT workloads.
- Canonical statement-to-provider resolution with exactly-one-match semantics.
- Source-, ABI-, template-, proof-, native-, target-, and plan-bound authority.
- Fail-closed handling of missing, ambiguous, stale, forged, or ineligible
  providers.
- Behavioral traversal receipts: an OptiX label or symbol name is not accepted
  as evidence that traversal occurred.
- Exact-output functional qualification across nine paper applications and
  fourteen canonical regions.
- Application-owned algorithm boundaries: V3 does not choose between RT-1A2
  and RT-2A1, FR and MT, or other distinct paper algorithms.
- Generic OptiX physical families for bounded selection, metric kNN, fixed
  radius graphs, AABB queries, grouped ray/triangle reductions, planar-map
  regions, aggregate hierarchy, and triangle summaries.
- Explicit, verified partner continuations where a computation includes typed
  Numba or host continuation stages.

## Compatibility

The Python source package version is now `3.0.0`. Existing v2-era examples and
reproduction material remain in the repository, but the root documentation and
production compiler front door now describe V3.

V3 does not expose arbitrary application callbacks through its production
physical interface. Unsupported semantics fail closed until a reusable,
app-neutral compiler provider is added with the required contracts and tests.

## Qualification

The frozen V3 qualification rebuilt a target-native OptiX library on Home
Linux, ran nine applications in fresh processes, checked exact outputs, rebuilt
canonical authority independently, and required complete behavioral OptiX
receipts. The GitHub release-surface audit covers 22 semantic statements, 40
canonical bindings, and 10 standalone providers.

## Performance statement

V3.0 does not claim universal speedup over V2-direct or author implementations.
The release preserves mixed cold and prepared results and requires performance
claims to bind the exact workload, lifecycle, baseline, source, native, and
machine. This boundary is part of the release, not an omission.

## Upgrade path

1. Install the V3 source checkout with `python3 -m pip install -e .`.
2. Run `python3 examples/current/v3_canonical_mapping.py`.
3. Read the [architecture](architecture.md) and
   [correctness model](correctness_and_extension.md).
4. On NVIDIA Linux, build the target-native provider with `make build-optix`.
5. Use the qualified validation path in
   [V3 release and installation](release.md).
