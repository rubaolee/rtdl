# Goal1404: v1.5.1 Collect-K Track Boundary

Date: 2026-05-06

## Decision

v1.5 keeps `COLLECT_K_BOUNDED` excluded from the standalone release surface.
The serious bounded-collection work moves to v1.5.1.

## Boundary

v1.5:

- release standalone RTDL for the supported Embree+OptiX surface
- exclude row-returning collection-dependent apps
- keep `COLLECT_K_BOUNDED` experimental

v1.5.1:

- define fail-closed bounded collection semantics
- prove native Embree and OptiX collection parity
- run same-contract collection benchmarks
- get external review before any stable promotion or public wording

v1.6-v2.0:

- partner API design
- first partner prototype
- partner conformance suite
- partner ecosystem hardening
- public partner-ready RTDL

## Release-Gate Impact

The standalone release gate now records `collect_k_bounded_followup_track` as
the v1.5.1 workstream. This keeps v1.5 focused and prevents accidental movement
of bounded collection into the partner-mechanism track.

## Validation Command

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1398_v1_5_standalone_release_gate_test \
  tests.goal1399_collect_k_bounded_resolution_test
```
