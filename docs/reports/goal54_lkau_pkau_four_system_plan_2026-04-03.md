# Goal 54 Plan: LKAU PKAU Four-System Closure

Date: 2026-04-03

## Summary

The next concrete reproduction gap to close is the first Lakes/Parks family
under the same accepted four-system comparison standard already used for Goal
50:

- PostGIS
- native C oracle
- Embree
- OptiX

The chosen target is the existing bounded Australia slice:

- paper label: `LKAU ⊲⊳ PKAU`
- source boundary: Goal 37 `sunshine_tiny`
- provenance: derived-input from live OSM Overpass `way` geometry only

## Why This Target

This is the highest-value next family because it is already:

- staged and convertible with checked-in code
- executable on Linux
- parity-clean between the oracle and Embree from Goal 37

It is therefore much lower risk than taking on a fresh continent-scale
acquisition path first.

## Planned Deliverables

1. `scripts/goal54_lkau_pkau_four_system.py`
   - run PostGIS, C oracle, Embree, and OptiX on the bounded Australia slice
2. `tests/goal54_lkau_pkau_four_system_test.py`
   - regression coverage for SQL shape and report wording
3. final Goal 54 report after the Linux run

## Current Boundary

The remote execution step is currently blocked in this shell by SSH
authentication failure to `192.168.1.20`. The harness and plan can still be
prepared locally and reviewed before that run.

## Acceptance

Goal 54 should only be published if:

1. the Linux run completes
2. PostGIS uses indexed plans
3. all four systems match for `lsi` and `pip`
4. the result is reviewed and approved by at least 2 AIs
