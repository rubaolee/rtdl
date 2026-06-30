# Goal1615 v1.6.4 COLLECT_K_BOUNDED Reduced-Copy Benchmark

## Verdict

ACCEPTED as reduced-copy/prepared-output benchmark evidence.

## Scope

- Primitive: `COLLECT_K_BOUNDED`
- Scope: `same_contract_input_materialization_delta_with_prepared_host_output`
- Backends: `fake_native, embree, optix`
- Required backends: `fake_native, embree, optix`
- Accepted metric: `input_materialization_count_delta`
- Timing is diagnostic only.

## Records

| Backend | Unique rows | Candidate rows | Iterations | Baseline materializations | Prepared materializations | Delta | Status |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| fake_native | 32 | 128 | 4 | 4 | 1 | 3 | pass |
| fake_native | 128 | 512 | 4 | 4 | 1 | 3 | pass |
| fake_native | 512 | 1024 | 4 | 4 | 1 | 3 | pass |
| embree | 32 | 128 | 4 | 4 | 1 | 3 | pass |
| embree | 128 | 512 | 4 | 4 | 1 | 3 | pass |
| embree | 512 | 1024 | 4 | 4 | 1 | 3 | pass |
| optix | 32 | 128 | 4 | 4 | 1 | 3 | pass |
| optix | 128 | 512 | 4 | 4 | 1 | 3 | pass |
| optix | 512 | 1024 | 4 | 4 | 1 | 3 | pass |

## Claim Boundary

Goal1615 is a collect-k reduced-copy/prepared-output benchmark evidence package. The accepted evidence is copy/materialization-count reduction under the measured same-contract wrapper paths. Timing is diagnostic only and does not authorize public speedup wording, whole-app speedup claims, broad RTX/GPU wording, true zero-copy wording, stable COLLECT_K_BOUNDED promotion, release tags, or release action.
