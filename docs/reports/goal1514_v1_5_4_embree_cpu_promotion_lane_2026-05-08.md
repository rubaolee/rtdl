# Goal 1514: Embree CPU Promotion Lane

## Verdict

Embree is the right non-GPU lane for semantic hardening while no NVIDIA pod is
available. The immediate Embree work should focus on local correctness,
fail-closed bounded collection, reduction parity, ABI/export checks, and
cross-platform runnability. It should not be used to make NVIDIA, broad RTX,
whole-app, or true zero-copy claims.

This report adds no new performance claim and does not promote
`COLLECT_K_BOUNDED` out of experimental status.

## Why Embree Now

Embree can validate the parts of Python+RTDL that do not require GPU hardware:

- app-name-free primitive contracts;
- `ANY_HIT` and `COUNT_HITS` semantics;
- compact reduction summaries;
- bounded row collection semantics;
- fail-closed overflow behavior;
- stable row schemas and row ordering;
- Python/native ABI routing;
- local build and test repeatability.

That makes Embree the CPU reference lane for deciding whether a primitive is
semantically ready before OptiX/pod work measures the corresponding GPU path.

## Embree Work Items

| Work item | CPU-only value | Acceptance signal | Not a claim |
| --- | --- | --- | --- |
| Bounded collection parity | Proves row output semantics before GPU timing | Empty, zero-capacity, exact-fit, and overflow cases pass | Not stable public promotion |
| Fail-closed overflow tests | Prevents silent truncation | Overflow reports metadata and refuses partial materialization | Not a performance claim |
| Reduction parity | Proves compact summaries match row-materialized references | `ANY_HIT`, `COUNT_HITS`, int reductions, and float reductions match references | Not whole-app acceleration |
| ABI/export checks | Keeps Python and native symbol contracts aligned | Required Embree symbols exist and names match wrappers | Not app-free native internals |
| App-group guard tests | Keeps reduction, split-contract, and bounded-collection apps separate | Docs/tests distinguish compact decisions from row outputs | Not broad app acceleration |
| Linux/Windows smoke slices | Finds path/build/runnability drift without pods | Same focused tests pass on Windows and local Linux | Not NVIDIA evidence |

## Recommended Local Test Slice

Run this slice on Windows:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest `
  tests.goal1316_v1_5_embree_candidate_collection_surface_test `
  tests.goal1317_v1_5_embree_native_candidate_collection_abi_test `
  tests.goal1416_v1_5_1_collect_k_native_parity_test `
  tests.goal1418_v1_5_1_collect_k_readiness_gate_test `
  tests.goal1509_v1_5_4_app_technical_docs_test `
  tests.goal1510_v1_5_4_non_pod_app_classification_test `
  tests.goal1511_v1_5_4_app_group_deep_dives_test
```

Run the equivalent slice on Linux:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1316_v1_5_embree_candidate_collection_surface_test \
  tests.goal1317_v1_5_embree_native_candidate_collection_abi_test \
  tests.goal1416_v1_5_1_collect_k_native_parity_test \
  tests.goal1418_v1_5_1_collect_k_readiness_gate_test \
  tests.goal1509_v1_5_4_app_technical_docs_test \
  tests.goal1510_v1_5_4_non_pod_app_classification_test \
  tests.goal1511_v1_5_4_app_group_deep_dives_test
```

If native Embree is available, add app-level Embree smoke/parity tests such as:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal715_embree_fixed_radius_summary_test \
  tests.goal717_embree_prepared_fixed_radius_summary_test \
  tests.goal720_embree_prepared_knn_rows_test \
  tests.goal723_event_hotspot_embree_summary_test \
  tests.goal724_service_coverage_embree_summary_test \
  tests.goal736_robot_collision_embree_scaled_test
```

## Promotion Boundary

Embree can tell us that a primitive contract is semantically clean. It cannot
tell us that the OptiX path is fast, that NVIDIA RT cores were used, or that a
GPU copy boundary disappeared. After Embree passes, OptiX still needs its own:

- real NVIDIA build/runtime validation;
- preflight acceptance;
- parity validation;
- native path/topology validation;
- stage profile artifacts;
- external review for public claims or release decisions.

## Possible Troubles

- A local machine may not have native Embree libraries. In that case, ABI and
  mocked wrapper tests still help, but native app evidence is unavailable.
- Embree row ordering can hide instability if tests only compare unordered
  sets. Bounded collection should keep deterministic ordering where the
  contract requires it.
- Exact-fit and overflow cases are more important than average cases for
  `COLLECT_K_BOUNDED`.
- Reduction modes must not be confused with witness-row modes.
- Passing Embree semantics does not imply OptiX performance.

## Claim Boundary

Goal1514 is CPU-only planning and validation guidance. It does not authorize
public speedup wording, broad RTX wording, whole-app claims, true zero-copy
wording, stable primitive promotion, experimental public promotion, partner
tensor handoff, release action, or NVIDIA performance claims.

