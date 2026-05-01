# Goal1203 Polygon Jaccard Chunk Policy

Date: 2026-05-01

## Problem

Goal1200 showed that `polygon_set_jaccard` was not stable across OptiX chunk sizes:

- chunk `1`: pass
- chunk `8`: pass
- chunk `64`: failed parity
- chunk `512`: pass

The chunk-64 failure missed candidates and changed the final Jaccard result. That means arbitrary chunk settings must not be treated as public claim evidence.

## Change

`scripts/goal877_polygon_overlap_optix_phase_profiler.py` now emits an explicit `chunk_policy` for Jaccard summary profiling:

- `public_safe`: chunk size is in the reviewed public-safe range `[512, 4096]`.
- `diagnostic_only`: chunk size is outside that range and may be useful for investigation, but cannot support public readiness or public speedup wording.

Diagnostic-only runs now exit successfully with status `diagnostic_chunk_config` instead of being mixed into ordinary pass/fail public evidence. This preserves diagnostics while preventing unsafe chunk settings from blocking or authorizing public claims by accident.

`scripts/goal1201_optix_slower_investigation_intake.py` now records `chunk_policy` when present and treats older Goal1200 chunk artifacts as `legacy_unclassified`.

## Validation

Focused tests:

`PYTHONPATH=src:. python3 -m unittest tests/goal877_polygon_overlap_optix_phase_profiler_test.py tests/goal1201_optix_slower_investigation_intake_test.py`

Result:

`Ran 14 tests ... OK`

## Boundary

This is a local classification and claim-boundary repair. It does not prove that Jaccard is faster on RTX, and it does not authorize public RTX speedup wording. A later pod rerun should use public-safe Jaccard chunks for claim-path evidence and reserve smaller chunks for diagnostics only.
