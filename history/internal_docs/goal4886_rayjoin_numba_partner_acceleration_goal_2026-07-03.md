# Goal4886: RayJoin Numba Partner Acceleration Plan

Date: 2026-07-03

Status: `in_progress`

## Objective

Build the first serious Numba partner engineering pass for the RayJoin
paper-reproduction app.

The starting point is the already-correct bounded RayJoin reproduction:

- Section 5.2 LSI through public RTDL planar-map LSI;
- Section 5.3 PIP / point-location through public RTDL planar-map
  point-location;
- Section 5.7 overlay through public RTDL LSI + public RTDL PIP + Python
  application-layer output-chain assembly.

Goal4886 does **not** try to re-prove correctness from scratch. It preserves the
current comparator and correctness gates, then uses Numba to accelerate the
Python-side application continuation where it is actually a bottleneck.

## Three Versions To Compare

| Version | Definition | Purpose |
| --- | --- | --- |
| `AuthorOfficial` | Patched author C++/CUDA/OptiX comparator currently used by the reproduction line | Author-source performance baseline |
| `Current RTDL` | Public RTDL LSI/PIP primitives + current Python app-layer overlay assembly | Current correct RTDL implementation |
| `RTDL+Numba` | Same public RTDL LSI/PIP primitives + Numba-accelerated app-layer continuation/assembly | First partner-accelerated RTDL implementation |

## Non-Negotiable Boundaries

- Do not change `src/rtdsl/**` or `src/native/**` for this goal.
- Do not change the `AuthorOfficial` comparator.
- Do not import or call `rtdsl.rayjoin_overlay` as evidence for generic public
  RTDL language capability.
- Do not change output semantics or formatting.
- Numba must accelerate only app-layer continuation/assembly work, not replace
  RTDL LSI/PIP primitives.
- Correctness gates must run before performance claims.

## Initial Performance Hypothesis

Goal4880's Australia representative public route reported:

| Phase | Seconds |
| --- | ---: |
| load/pack left | 71.937 |
| load/pack right | 5.727 |
| public LSI rows | 5.694 |
| vertex PIP map0 in map1 | 10.737 |
| vertex PIP map1 in map0 | 1.556 |
| output-chain write | 17.259 |
| total elapsed | 118.497 |

Numba should not be used to claim victory over:

- text CDB parsing/loading;
- file I/O and string formatting;
- native RTDL LSI/PIP traversal.

The first reasonable Numba targets are:

1. numeric midpoint generation and filtering;
2. edge-local intersection grouping metadata;
3. output-chain keep/flush decision precomputation;
4. point/face array compaction and mapping support;
5. any repeated Python loops that transform RTDL rows into app-layer arrays.

If file writing dominates `output_chain_write_sec`, Numba may improve only the
pre-writer assembly part, not total wall time. That must be reported honestly.

## Work Plan

### A. Document And Freeze Current Route

Produce this goal file and pin the current correct route:

```text
history/internal_docs/goal4880_section57_public_primitives_overlay_harness.py
```

Current correctness anchor:

```text
history/internal_docs/goal4883_section57_final_bounded_reproduction_packet_2026-07-03.md
```

Exit gate:

- no ambiguity about comparator;
- no ambiguity about current RTDL route;
- no Numba correctness claim yet.

### B. Add Numba Kernel Layer For App Continuation

Create a small Numba partner module under `history/internal_docs/` first, so it
does not prematurely become public API.

Planned artifact:

```text
history/internal_docs/goal4886_rayjoin_numba_overlay_kernels.py
```

Initial kernels:

- midpoint generation from sorted edge-local intersections;
- consecutive point dedupe / emitted point counting;
- chain keep/face-composition precomputation where representable as arrays.

Exit gate:

- pure Python reference and Numba result match on controlled synthetic cases;
- Numba absence fails closed or uses Python reference without changing result.

### C. Add A Numba-Optional Harness

Create a Numba-enabled sibling harness rather than editing the already-correct
Goal4880 harness in place.

Planned artifact:

```text
history/internal_docs/goal4886_section57_public_primitives_overlay_numba_harness.py
```

The harness must emit:

- route label: `public_rtdl_lsi_pip_plus_numba_partner_app_continuation`;
- phase timing for Python-compatible and Numba-assisted sections;
- correctness hash/byte equality against the same comparator;
- explicit flag `numba_on_app_continuation_path: true`;
- explicit flag `numba_on_rtdl_primitive_path: false`.

Exit gate:

- byte-equal output on at least one already-passing representative pair;
- phase timing table includes both current RTDL and RTDL+Numba.

### D. Controlled Performance Comparison

Run three-way comparison:

```text
AuthorOfficial
Current RTDL
RTDL+Numba
```

Preferred first dataset:

```text
Australia Lakes x Parks representative
```

Reason:

- already byte-equal;
- smaller than full US streams;
- enough output-chain work to expose Python app-layer overhead.

If POD is available, repeat on one larger available pair or a bounded slice.

Exit gate:

- correctness passes first;
- phase timing explains where Numba helps or fails;
- no broad RayJoin speedup claim before more data.

## Acceptance Criteria

Goal4886 can close only if it produces:

1. a documented Numba partner plan and implementation artifact;
2. synthetic parity tests for Numba kernels against Python reference;
3. a Numba-enabled harness or a documented blocker explaining why the current
   app-layer structure is not yet suitable;
4. at least one correctness-preserving run, or a clear statement that POD/data
   execution is required next;
5. no runtime/core edits;
6. a call-for-review packet for external review.

## Expected Output Files

| File | Purpose |
| --- | --- |
| `history/internal_docs/goal4886_rayjoin_numba_partner_acceleration_goal_2026-07-03.md` | This goal definition |
| `history/internal_docs/goal4886_rayjoin_numba_overlay_kernels.py` | Numba partner kernels and Python reference fallbacks |
| `history/internal_docs/goal4886_section57_public_primitives_overlay_numba_harness.py` | Numba-enabled reproduction harness |
| `history/internal_docs/goal4886_numba_synthetic_parity_summary.json` | Synthetic parity evidence |
| `history/internal_docs/goal4886_rayjoin_numba_partner_acceleration_report_2026-07-03.md` | Completion report |
| `history/internal_docs/call_for_review_goal4886_rayjoin_numba_partner_acceleration_2026-07-03.md` | Review request |

## Exit Labels

Allowed:

- `completed_numba_partner_app_continuation_acceleration_with_correctness_gate`
- `completed_numba_kernel_parity_only__pod_performance_required_next`
- `blocked_by_current_app_structure_not_numba_ready`
- `blocked_by_missing_pod_or_dataset_for_performance`

Not allowed:

- `numba_proves_full_rayjoin_speedup`
- `numba_replaces_rtdl_primitives`
- `authorofficial_beaten_broadly`
- `full_hidden_input_reproduction`
