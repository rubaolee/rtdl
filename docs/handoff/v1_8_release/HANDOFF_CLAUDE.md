# RTDL Handoff For Claude

Date: 2026-05-10

Project directory:

```text
C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review
```

Pod staged directory:

```text
/tmp/rtdl_goal167x_validate
```

## Required Context

- Read `C:\Users\Lestat\Desktop\refresh.md` first if starting fresh.
- Work on RTDL `main`.
- Roadmap: `v1.8` finishes Python+RTDL; `v2.0` finishes Python+partner+RTDL.
- RTDL engine must stay absolutely app-agnostic.
- Partner consensus: protocol first, PyTorch reference first, CuPy conformance alongside it.
- Do not touch untracked `docs/reports/goal1204_rtdl_source_2026-05-01.tar.gz`.

## Current State

- Focused current gate: `68` tests pass, `1` skipped.
- Current app-shaped native callable/export gap: `83` real symbols.
- Remaining native leakage families:
  - `db`: 30
  - `polygon`: 29
  - `knn`: 14
  - `bfs`: 10
- Strict native scan currently reports `92` unique symbols and `178` occurrences, including `9` unique / `14` occurrence uppercase `RTDL_DB_*` enum constant false positives.
- `git diff --check` passes with only CRLF warnings.

## Completed Work

- Added v1.8/v2.0 roadmap gate:
  - `docs/release_reports/v1_8_v2_0_python_partner_rtdl_gate.md`
  - `tests/goal1671_v1_8_v2_0_partner_gate_test.py`
- Added Goal1672 native leakage migration classification:
  - `docs/reports/goal1672_native_app_leakage_migration_classification_2026-05-10.md`
  - `docs/reports/goal1672_native_app_leakage_migration_classification_2026-05-10.json`
  - `tests/goal1672_native_app_leakage_migration_classification_test.py`
- Completed Goal1673 OptiX pose-to-group native source migration:
  - native OptiX pose-shaped exports renamed to generic group-shaped exports;
  - Python compatibility aliases remain in `src/rtdsl/optix_runtime.py`;
  - generic Python path uses group names directly.
- Completed Goal1674 oracle root wrapper quarantine:
  - `src/native/oracle/rtdl_oracle_polygon.cpp` removed/renamed to `src/native/oracle/rtdl_oracle_geometry_cells.cpp`;
  - `src/native/rtdl_oracle.cpp` include updated.
- Added Goal1675 partner substrate:
  - `src/rtdsl/partner.py`
  - exports in `src/rtdsl/__init__.py`
  - generic DLPack adapter, PyTorch shell, CuPy shell, fallback policies, borrowed pointer extraction.
- Added Goal1676 regression guard for removed pose/oracle native names.
- Added Goal1677 pod partner smoke report/test.
- Added Goal1678 pod Embree build report/test.
- Added Goal1679 broad pod full-suite triage report/test.
- Added Goal1680 current native app-leakage gap report/test.
- Fixed stale Goal760 test expectation for `packed_arrays` now accepting both `embree` and `optix`.
- Completed Goal1681 PIP-to-point-primitive-anyhit native source migration:
  - all six `pip`-family native callables/exports renamed to
    `rtdl_<engine>_run_point_primitive_anyhit_packet` across Embree, HIPRT,
    OptiX, Oracle, and Vulkan;
  - HIPRT internal kernel filename hint renamed from `rtdl_hiprt_pip_2d.cu`
    to `rtdl_hiprt_point_primitive_anyhit_2d.cu`;
  - Python runtimes (`embree_runtime.py`, `hiprt_runtime.py`,
    `optix_runtime.py`, `oracle_runtime.py`, `vulkan_runtime.py`) updated to
    bind the renamed symbols;
  - `_run_point_primitive_anyhit_packet` added to
    `_GENERIC_NATIVE_SYMBOL_FRAGMENTS` in
    `src/rtdsl/python_rtdl_app_purity.py`;
  - `docs/reports/goal1681_pip_to_point_primitive_anyhit_native_migration_2026-05-10.md`;
  - `tests/goal1681_pip_to_point_primitive_anyhit_native_migration_test.py`;
  - Goal1672 report updated to record the Goal1681 follow-up;
  - Goal1680 report and test updated to the new totals (93/180/84);
  - v1.7 gate report links Goal1681;
  - Goal1603 test updated to require the renamed exports and forbid the
    removed `pip` names;
  - Goal1658 audit test threshold lowered from `>= 40` to `>= 38` to track
    the two legacy symbols dropped by the migration.

- Completed Goal1682 Hausdorff-to-max-distance-nearest-candidate native source migration:
  - the single `rtdl_embree_run_directed_hausdorff_2d` native export was
    renamed to `rtdl_embree_run_max_distance_nearest_candidate_2d`;
  - Hausdorff semantics retained in Python `directed_hausdorff_2d_embree`
    helper; native ABI no longer encodes the `hausdorff` term;
  - `src/rtdsl/embree_runtime.py` updated to bind the renamed symbol and
    the optional argtypes/restype config block was renamed accordingly;
  - `_run_max_distance_nearest_candidate_2d` added to
    `_GENERIC_NATIVE_SYMBOL_FRAGMENTS` in
    `src/rtdsl/python_rtdl_app_purity.py`;
  - `docs/reports/goal1682_hausdorff_to_max_distance_nearest_candidate_native_migration_2026-05-10.md`;
  - `tests/goal1682_hausdorff_to_max_distance_nearest_candidate_native_migration_test.py`;
  - Goal1672 report updated to record the Goal1682 follow-up;
  - Goal1680 report and test updated to the new totals (92/178/83);
  - v1.7 gate report links Goal1682;
  - Goal1603 / Goal1668 / Goal1676 / Goal722 / Goal1658 tests updated to
    expect the renamed Embree export and a lowered legacy threshold
    (`>= 37` after dropping the legacy `rtdl_optix_run_pip`,
    `rtdl_embree_run_directed_hausdorff_2d` references).

## Pod Results

Pod access used key from:

```text
Z:\rtdl-dev\id_ed25519_rtdl_codex
```

Environment:

- GPU: NVIDIA RTX A5000
- Driver: 570.211.01
- Python: 3.11.10
- `nvcc`: `/usr/local/cuda-12.4/bin/nvcc`

Passed on pod:

- Focused v1.8/v2.0 gate: `49` tests pass, `1` skipped.
- `make build`
- `make build-embree` after installing:

```text
apt-get install -y libembree-dev libgeos-dev
```

Embree result:

```text
Embree 3.12.2
```

Partner smoke:

- real PyTorch CUDA smoke passed with `torch 2.4.1+cu124`;
- real CuPy CUDA smoke passed in isolated venv `/tmp/rtdl_goal167x_cupy_venv` with `cupy 14.0.1`.

Blocked on pod:

- `make build-optix` fails because OptiX SDK headers are missing at `/opt/optix/include/optix.h`.
- CUDA/nvcc exists; missing piece is OptiX SDK headers or a compatible prebuilt `librtdl_optix.so`.

Broad pod discovery:

```text
Ran 3613 tests in 332.008s
FAILED (failures=65, errors=31, skipped=283)
```

Triage: dominated by stale historical public-doc/release pinning tests and OptiX-dependency-sensitive tests; not a v1.8 release pass.

## Recent Verification

Focused local gate:

```powershell
$env:PYTHONPATH='src'
py -3 -m unittest tests.goal1603_v1_6_stable_native_path_app_leakage_audit_test tests.goal1668_native_engine_app_agnostic_directive_test tests.goal1669_python_partner_rtdl_partner_choice_architecture_test tests.goal1670_all_external_partner_analysis_consensus_test tests.goal1671_v1_8_v2_0_partner_gate_test tests.goal1672_native_app_leakage_migration_classification_test tests.goal1673_optix_pose_to_group_native_migration_test tests.goal1674_oracle_root_wrapper_quarantine_test tests.goal1675_partner_protocol_substrate_test tests.goal1676_native_leakage_delta_regression_test tests.goal1677_partner_pod_smoke_test tests.goal1678_python_rtdl_pod_embree_build_test tests.goal1679_pod_full_suite_triage_test tests.goal1680_current_native_app_leakage_gap_test tests.goal1681_pip_to_point_primitive_anyhit_native_migration_test tests.goal1682_hausdorff_to_max_distance_nearest_candidate_native_migration_test
```

Result:

```text
Ran 68 tests
OK (skipped=1)
```

Other checks:

```powershell
py -3 -m py_compile src\rtdsl\partner.py src\rtdsl\optix_runtime.py src\rtdsl\embree_runtime.py src\rtdsl\hiprt_runtime.py src\rtdsl\oracle_runtime.py src\rtdsl\vulkan_runtime.py src\rtdsl\python_rtdl_app_purity.py src\rtdsl\generic_primitives.py src\rtdsl\__init__.py
git diff --check
```

Both pass; `git diff --check` only reports CRLF warnings.

## Recommended Next Work

No pod is needed for the next useful slice.

The Goal1681 PIP migration is done; the next smallest remaining family is
`hausdorff` (1 symbol), followed by `bfs` (10), `knn` (14), `polygon` (29),
and `db` (30).

The Goal1682 Hausdorff migration is done; remaining families ranked by
size: `bfs` (10 symbols), `knn` (14), `polygon` (29), `db` (30).

Goal1683 candidate:

- start the `bfs` (10 symbols) migration into generic frontier/edge packet
  traversal, per Goal1672's `frontier_edge_traversal` direction;
- add a Goal1683 report/test;
- update the current native leakage gap counts (83 → 73 real symbols if
  all 10 bfs symbols are migrated);
- do not claim fully app-agnostic native internals until the release-surface
  scan reaches zero or remaining historical symbols are mechanically
  quarantined outside public runners.

Alternative Goal1683 candidates:

- start the `knn` (14 symbols) migration into generic bounded candidate
  collection plus app-owned nearest-neighbor interpretation, per Goal1672's
  `bounded_nearest_candidate_collection` direction;
- start the `polygon` (29 symbols) migration into generic geometry candidate
  packets and reduction descriptors;
- start the `db` (30 symbols) migration into generic columnar predicate
  packets and grouped reduction descriptors.

Need pod again only when:

- OptiX SDK headers are available and `OPTIX_PREFIX` can point to a
  directory containing `include/optix.h`; or
- a compatible prebuilt `librtdl_optix.so` is provided through
  `RTDL_OPTIX_LIB`; or
- the renamed `rtdl_<engine>_run_point_primitive_anyhit_packet` exports
  need a hardware rebuild/runtime smoke per backend.
