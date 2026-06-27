# Goal623: v0.9.4 Backend Naming And Apple DB Boundary

Date: 2026-04-19

Status: implemented and externally accepted by Gemini Flash and Claude.

## Purpose

Clarify the public documentation answer to two release-facing questions:

1. Whether HIPRT and Apple RT are now two newer RTDL backend families.
2. Whether RTDL database and graph workloads on Apple Silicon use Apple
   ray-tracing hardware.

## Decision

Yes, HIPRT and Apple RT are two newer RTDL backend families, alongside CPU /
oracle, Embree, OptiX, and Vulkan.

The Apple RT name is a backend-family name, not a claim that every Apple
workload uses Apple ray-tracing hardware. Current Apple geometry and
nearest-neighbor slices use Apple MPS ray-intersection paths. Current bounded
DB and graph slices use Apple Metal compute or Metal-filter-plus-CPU
native-assisted paths.

Therefore, RTDL must not claim that current Apple `conjunctive_scan`,
`grouped_count`, `grouped_sum`, `bfs_discover`, or `triangle_match` execution is
Apple ray-tracing-hardware traversal.

## Public Documentation Updates

Updated files:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/quick_tutorial.md`
- `/Users/rl2025/rtdl_python_only/docs/capability_boundaries.md`
- `/Users/rl2025/rtdl_python_only/docs/backend_maturity.md`
- `/Users/rl2025/rtdl_python_only/docs/current_architecture.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/examples/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9_4/support_matrix.md`

The edits add explicit wording that:

- HIPRT and Apple RT are the two newer backend families.
- HIPRT remains Linux HIPRT-SDK/CUDA-path validated, with no AMD GPU validation,
  no HIPRT CPU fallback, and no broad RT-core speedup claim.
- Apple RT uses MPS RT for supported geometry and nearest-neighbor slices.
- Apple DB and graph rows use Metal compute/native-assisted paths, not Apple
  MPS ray-tracing traversal.
- `native_only=True` should be used when applications must reject unsupported
  shape/backend combinations.

## Stale Wording Fixed

`/Users/rl2025/rtdl_python_only/docs/quick_tutorial.md` still described the
Apple line as "current v0.9.2 candidate" and described unsupported rows as
`cpu_reference_compat`. That was stale after the v0.9.4 target absorbed the
internal v0.9.2/v0.9.3 evidence and moved all 18 rows to explicit native or
native-assisted Apple modes. The tutorial now points to the current v0.9.4
target and its MPS RT versus Metal compute split.

## Validation

Validation run:

```text
rg -n 'current v0\.9\.2|current `v0\.9\.2|Apple hardware execution|cpu_reference_compat' \
  README.md docs/README.md docs/quick_tutorial.md docs/rtdl_feature_guide.md \
  docs/capability_boundaries.md docs/current_architecture.md \
  docs/backend_maturity.md docs/release_facing_examples.md examples/README.md
```

Result: no matches.

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal512_public_doc_smoke_audit_test \
  tests.goal511_feature_guide_v08_refresh_test \
  tests.goal531_v0_8_release_candidate_public_links_test -v
```

Result: 9 tests OK.

```text
PYTHONPATH=src:. python3 scripts/goal497_public_entry_smoke_check.py
```

Result: valid true.

```text
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
PYTHONPATH=src:. python3 -m unittest tests.goal515_public_command_truth_audit_test -v
```

Result: public command truth valid true; 244 commands across 14 public docs;
1 test OK. The generated Goal515 audit artifacts were refreshed only for
line-number drift caused by the README wording insertion.

```text
git diff --check
```

Result: no whitespace errors.

## Honesty Boundary

Allowed wording:

> HIPRT and Apple RT are two newer RTDL backend families. Apple RT currently
> uses MPS RT for supported geometry/nearest-neighbor slices and Metal
> compute/native-assisted paths for bounded DB and graph slices.

Disallowed wording:

> Apple DB workloads are accelerated by Apple ray-tracing hardware.

Disallowed wording:

> Apple RT is a broadly optimized or mature backend comparable to Embree.

## External Consensus

Gemini 2.5 Flash wrote:

```text
VERDICT: ACCEPT

RATIONALE: The document "goal623_v0_9_4_backend_naming_and_apple_db_boundary_2026-04-19.md" correctly states that HIPRT and Apple RT are newer RTDL backend families. It also honestly distinguishes Apple MPS RT geometry/nearest-neighbor paths from Apple Metal compute/native-assisted DB and graph paths, explicitly detailing what is and is not accelerated by Apple ray-tracing hardware. The "Honesty Boundary" section further clarifies acceptable and unacceptable wording.
```

Claude wrote:

```text
Verdict: ACCEPT
```

Claude additionally confirmed that the docs consistently name HIPRT and Apple
RT as newer backend families and that the support matrix, capability boundary,
backend maturity, and architecture docs explicitly separate Apple MPS RT
geometry/nearest-neighbor paths from Apple Metal compute/native-assisted DB and
graph paths.
