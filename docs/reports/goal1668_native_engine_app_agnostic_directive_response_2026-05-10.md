# Goal1668 Native-Engine App-Agnostic Directive Response

Date: 2026-05-10

Source directive:

- `Z:\goal1668_antigravity_directive_app_agnostic_engine_2026-05-10.md`
- repo snapshot:
  `docs/directives/goal1668_antigravity_directive_app_agnostic_engine_2026-05-10.md`
- author: Antigravity / Gemini
- status in this repo: accepted as a mandatory next-track architectural gate

Repository under test:

- commit before this response: `b019449197bfbee9e3d988a7c618cbba36351dc5`
- branch: `main`

## Verdict

The directive is architecturally correct and should be adopted for the
v1.7-v2.0 track.

The current RTDL public Python+RTDL surface can still be described as
app-generic at the stable primitive-contract level, but the native tree is not
fully app-agnostic. A strict native-symbol regex audit still finds app-shaped,
domain-shaped, and workload-shaped native names.

Therefore:

- `v1.6.11` may keep narrow wording about app-generic public primitive
  contracts.
- Current RTDL must not claim that native internals are fully app-agnostic.
- The next architectural release gate must fail unless app-shaped native
  leakage is either removed or formally quarantined outside the native engine
  release surface.

## Phase 1: Purge Audit Executed

Audit scope:

- all files under `src/native/`
- scanned symbol-like tokens matching `rtdl_[A-Za-z0-9_]+`
- leakage terms from the directive:
  - `db`
  - `pip`
  - `bfs`
  - `robot`
  - `pose`
  - `polygon`
  - `knn`
  - `hausdorff`
  - `jaccard`

Result:

- unique matched symbols: `96`
- full machine-readable dirty-baseline manifest:
  `docs/reports/goal1668_native_leakage_manifest_baseline_2026-05-10.json`
- current status: `NOT ZERO`
- gate implication: native internals are not app-agnostic today

Counts by leakage term:

| Term | Unique symbol count |
| --- | ---: |
| `db` | 30 |
| `pip` | 6 |
| `bfs` | 10 |
| `robot` | 0 |
| `pose` | 5 |
| `polygon` | 30 |
| `knn` | 14 |
| `hausdorff` | 1 |
| `jaccard` | 2 |

Counts by backend family:

| Backend family | Unique symbol count |
| --- | ---: |
| Apple RT | 4 |
| Embree | 17 |
| HIPRT | 12 |
| OptiX | 32 |
| Oracle/native CPU | 15 |
| Vulkan | 12 |
| Other/native wrapper | 4 |

The backend-family table counts the 96 unique leaked symbols used for the
release-gate baseline. The machine-readable manifest stores 187 concrete hit
occurrences, so its per-backend occurrence counts may be larger when the same
symbol appears in declarations, definitions, error strings, shader source
strings, or helper calls.

Representative leakage examples:

- `rtdl_optix_db_dataset_compact_summary_batch`
- `rtdl_optix_prepare_pose_indices_2d`
- `rtdl_optix_run_bfs_expand`
- `rtdl_embree_run_directed_hausdorff_2d`
- `rtdl_embree_collect_polygon_pair_candidates_bounded`
- `rtdl_hiprt_run_segment_polygon_hitcount`
- `rtdl_vulkan_db_dataset_grouped_sum`
- `rtdl_apple_rt_run_db_conjunctive_scan_numeric_compute`
- `rtdl_oracle_run_polygon_set_jaccard`

Interpretation:

These names include real app/workload vocabulary in native exports or native
implementation surfaces. Some are compatibility or proof paths, and some are
older validated workload helpers. That history does not make them acceptable
for a future claim that the native engine is app-agnostic.

## Phase 2: Complete Decoupling Plan

The directive's target state is accepted:

```text
Python owns domain lowering.
The native engine owns only generic primitives and reductions.
```

Required native API direction:

| Current leaked shape | Future acceptable shape |
| --- | --- |
| `db_*`, `*_conjunctive_scan`, app-specific table helpers | generic row/filter/reduction packets, if kept native at all |
| `bfs_*`, graph-specific expansion helpers | generic frontier/edge primitive packets or Python/partner-owned graph lowering |
| `pose_*`, robot-specific prepared indices | generic ray packet preparation and generic grouped reductions |
| `polygon_*`, `pip`, `jaccard`, `hausdorff` exports | generic geometric candidate collection, any-hit/count/closest-hit, bounded collection, and generic reductions |
| `knn_rows` app/workload surface | generic bounded collection / nearest candidate primitive with app-owned interpretation |

Required classification for all stable apps:

- `fully_generic`: app lowers to primitive packets and generic reductions only
- `scalar_only`: app consumes a generic scalar/count/reduction result without
  app-shaped native code
- `blocked`: app still depends on app-shaped native internals and cannot be
  used as evidence for app-agnostic native internals

Rules:

- Do not hide leaked native code behind nicer Python wrapper names.
- Do not restore app-specific CUDA/C++ backdoors to recover performance.
- Do not authorize public wording that says native internals are fully
  app-agnostic until the audit count is zero or quarantined exports are outside
  the release surface by construction.

## Phase 3: Partner Mechanism And Zero-Copy Performance Rescue

The performance rescue path is not app-specific native code.

Accepted direction:

- partner tensor handoff for PyTorch/CuPy/Numba-style memory owners
- true zero-copy or reduced-copy transfer paths where the platform allows it
- generic prepared input/output buffers
- generic collection/reduction primitives with strict parity tests

This means future performance work should optimize the data path into generic
RTDL primitives, not reintroduce database, graph, robot, or GIS logic inside
C++/CUDA backend entry points.

## Required Release Gate

The v1.7 or v2.0 release gate must fail unless a superseding report proves one
of the following:

1. strict audit result is zero for app/domain/workload leakage terms in
   release-surface native exports, or
2. remaining historical symbols are mechanically quarantined outside the native
   release surface and cannot be linked or called by public runners.

Quarantine is an interim migration tool, not a permanent architecture. Any
quarantined legacy native app-shaped surface must have a deletion/sunset plan
before the v2.0 app-agnostic native-engine claim is authorized.

The next expanded audit should also check semantic leakage beyond the initial
directive terms, including at least `table`, `column`, `edge`, `vertex`,
`agent`, and `trajectory`, with false positives documented explicitly instead
of silently ignored.

Until then, blocked wording remains:

```text
RTDL native internals are fully app-agnostic.
```

Allowed interim wording remains:

```text
RTDL's current public Python+RTDL surface is app-generic at the stable
primitive-contract level, while older app-shaped native compatibility/proof
paths remain excluded from that claim.
```

## Immediate Operations Completed

- Read and accepted the Antigravity/Gemini directive from `Z:`.
- Executed the strict Phase 1 regex audit over `src/native/`.
- Confirmed non-zero native app/domain leakage.
- Wrote this response report.
- Added a v1.7 app-agnostic native-engine release gate document.
- Added a machine-readable dirty-baseline leakage manifest.
- Added a regression test so the directive remains visible and the current
  blocked claim cannot be accidentally authorized.

## Next Engineering Work

1. Generate a complete machine-readable native export manifest.
2. Classify each leaked symbol as remove, rename-to-generic, replace-by-packet,
   or quarantine.
3. Choose one high-value app path and migrate it from leaked native helper to
   generic primitive packets.
4. Repeat until all public runners are free of app-shaped native calls.
5. Re-run the strict audit and require zero/quarantine before v1.7/v2.0 release
   wording.

This is a major architectural track, not a one-commit cleanup.
