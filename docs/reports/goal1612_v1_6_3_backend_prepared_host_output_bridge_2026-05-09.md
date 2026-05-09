# Goal1612 v1.6.3 Backend Prepared Host-Output Bridge

## Verdict

ACCEPTED as backend bridge evidence.

## Scope

- Version slot: `v1.6.3`
- Backends: `fake_native, embree, optix`
- Required backends: `fake_native`
- Real backend skips are allowed only when the backend is not required.
- Timing is diagnostic only.

## Records

| Backend | Status | Rows | Iterations | Baseline input materializations | Prepared input materializations | Delta | Skip reason |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| fake_native | pass | 256 | 5 | 5 | 1 | 4 |  |
| embree | pass | 256 | 5 | 5 | 1 | 4 |  |
| optix | skipped | 256 | 5 |  |  |  | FileNotFoundError: librtdl_optix not found.  Build it with 'make build-optix' or set RTDL_OPTIX_LIB=/path/to/lib. |

## Claim Boundary

Goal1612 is a backend bridge for the prepared host-output measurement path. It may record fake-native, Embree, or OptiX execution/skip records under the Goal1610/Goal1611 schema. It does not authorize performance claims, public speedup wording, whole-app speedup claims, broad RTX wording, true zero-copy wording, stable COLLECT_K_BOUNDED promotion, partner tensor handoff, package install claims, release tags, or release action.
