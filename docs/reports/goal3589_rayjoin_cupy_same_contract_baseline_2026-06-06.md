# Goal3589: RayJoin CuPy Same-Contract Baseline

Date: 2026-06-06

## Purpose

Goal3586 made RayJoin readable as one app score by composing the three promoted
hot RTDL/OptiX routes:

- PIP positive assignment count/refinement
- LSI dense left-id count
- overlay active pair-dependency count

That score compared RTDL/OptiX against Embree. Goal3589 adds the harder
fairness check: compare the same promoted RTDL/OptiX hot routes against dense
CuPy CUDA-core all-pairs baselines for the same authored tiled fixtures.

This is intentionally user/partner code outside the engine. The CuPy baseline
does not use RT cores and does not call RTDL candidate generators.

## Measurement Protocol

Script:
`scripts/goal3589_rayjoin_cupy_same_contract_baseline.py`

Artifacts:

- `docs/reports/goal3589_rayjoin_cupy_same_contract_baseline_a5000/summary.json`
- `docs/reports/goal3589_rayjoin_cupy_same_contract_baseline_stress_a5000/summary.json`

Hardware:

- NVIDIA RTX A5000
- source commit: `fda11cb743b3a57eb913e9e553d206c9c2ce208b`

Protocol:

- one warmup
- five measured hot repeats
- RTDL/OptiX reports `phases_sec.prepared_query_sec`
- CuPy reports warmed dense RawKernel plus device reduction time
- setup/compile/upload are excluded from both primary hot medians
- count identity must match for every row

## Standard Packet

Dataset tier: `x512`

| Contract | Candidate pairs | CuPy CUDA-core sec | RTDL/OptiX sec | RTDL/OptiX speedup vs CuPy | Count |
| --- | ---: | ---: | ---: | ---: | ---: |
| PIP positive assignment count/refinement | 524288 | 0.000071101 | 0.001731914 | 0.041x | 512 |
| LSI dense left-id count | 262144 | 0.000071960 | 0.000094119 | 0.765x | 512 |
| Overlay active pair-dependency count | 262144 | 0.000061321 | 0.000327377 | 0.187x | 512 |

Geometric mean RTDL/OptiX speedup vs CuPy: **0.180x**.

All counts matched.

## Stress Packet

Dataset tier: `x2048`

| Contract | Candidate pairs | CuPy CUDA-core sec | RTDL/OptiX sec | RTDL/OptiX speedup vs CuPy | Count |
| --- | ---: | ---: | ---: | ---: | ---: |
| PIP positive assignment count/refinement | 8388608 | 0.000302662 | 0.005827603 | 0.052x | 2048 |
| LSI dense left-id count | 4194304 | 0.000768234 | 0.000122694 | 6.261x | 2048 |
| Overlay active pair-dependency count | 4194304 | 0.000112117 | 0.001180309 | 0.095x | 2048 |

Geometric mean RTDL/OptiX speedup vs CuPy: **0.314x**.

All counts matched.

## Interpretation

This is a useful negative result.

The Goal3586 Embree comparison remains true: the promoted RayJoin-style RTDL
routes are dramatically faster than Embree on these authored hot contracts.

But Goal3589 shows that Embree is not the only serious baseline. A warmed CuPy
CUDA-core user baseline beats the current RTDL/OptiX route for PIP and overlay
active-count on the simple square tiled fixtures. RTDL/OptiX wins the stress LSI
row, where RT traversal and dense left-id count produce a real advantage over
the dense CUDA-core pair test.

The reason is not mysterious:

- The authored PIP and overlay fixtures are geometrically simple and sparse.
- The dense CuPy kernels do a cheap bounds rejection for almost every pair.
- RTDL/OptiX still pays traversal and continuation overhead, and PIP also pays
  an exact CuPy refinement step after RT candidate generation.
- RT cores become more plausible when traversal rejects complex geometry better
  than a simple CUDA bounds/grid kernel, or when RTDL keeps richer downstream
  continuation resident.

## Design Consequence

RayJoin cannot currently be advertised as "RTDL/OptiX beats serious CUDA-core
user code" on these simple authored fixtures.

The next performance work should target one of these paths:

1. Use richer RayJoin-style geometry where dense CUDA all-pairs bounds rejection
   is no longer the whole problem.
2. Add a generic cheap bounds/grid prefilter front door so RTDL can choose a
   non-RT primitive when the RT path is the wrong tool.
3. Improve PIP and overlay continuation so RT traversal output feeds a stronger
   device-resident exact/refinement path with less per-query overhead.

This is still compatible with the app-agnostic engine rule. The engine should
not learn RayJoin, but it may expose generic shape-pair prefilters,
closed-shape membership continuations, and device-resident reductions that make
the right path cheap for user applications.

## Boundaries

This goal does not authorize:

- a RayJoin paper reproduction claim;
- a claim that RTDL beats the original RayJoin implementation;
- a public RT-core speedup claim for RayJoin;
- a whole-app speedup claim;
- a release authorization;
- a true zero-copy claim.

It authorizes an internal benchmark conclusion: the current RayJoin promoted
routes need a serious CUDA-core same-contract baseline in every future
performance packet, and the current simple PIP/overlay authored fixtures are not
strong RT-core wins.

## Validation

Validation test:
`tests/goal3589_rayjoin_cupy_same_contract_baseline_test.py`

The test enforces the dry-run schema, the non-RT CuPy baseline classification,
the same-contract markers, and the claim-boundary flags. The A5000 artifacts
are optional for local test runs but checked when present.
