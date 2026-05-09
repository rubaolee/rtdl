# RTDL v1.6 Support Matrix

Status: released v1.6 support matrix. The `v1.6` annotated tag was published
after final 3-AI release consensus and explicit release/tag authorization.

This matrix records the v1.6 Python+RTDL architecture closure surface. It is
narrower than the general current-main feature set and intentionally excludes
experimental, proof, partner, and broad app-speedup claims.

## Stable Primitive Surface

| Primitive | Public status | Backends | Boundary |
| --- | --- | --- | --- |
| `ANY_HIT` | stable v1.6 primitive | Embree, OptiX | RT-shaped any-hit predicate; no whole-app claim |
| `COUNT_HITS` | stable v1.6 primitive | Embree, OptiX | RT-shaped hit-count predicate; no broad graph/GIS/DB claim |
| `REDUCE_FLOAT(MIN)` | stable v1.6 primitive | Embree, OptiX where validated | exact reviewed primitive subpaths only |
| `REDUCE_FLOAT(MAX)` | stable v1.6 primitive | Embree, OptiX where validated | exact reviewed primitive subpaths only |
| `REDUCE_FLOAT(SUM)` | stable v1.6 primitive | Embree, OptiX where validated | exact reviewed primitive subpaths only |
| `REDUCE_INT(COUNT)` | stable v1.6 primitive | Embree, OptiX where validated | exact reviewed primitive subpaths only |
| `REDUCE_INT(SUM)` | stable v1.6 primitive | Embree, OptiX where validated | exact reviewed primitive subpaths only |

## Pending Or Excluded Surfaces

| Surface | v1.6 status | Reason |
| --- | --- | --- |
| `COLLECT_K_BOUNDED` | pending/experimental | needs separate promotion gate, bounds tests, parity, benchmarks, and external review |
| True zero-copy | excluded | no measured GPU-resident or externally shareable device-memory claim gate |
| Partner tensor handoff | excluded | starts in the Python+partner+RTDL track after v1.6 |
| Package install | excluded | no validated packaging metadata |
| Whole-app speedup | excluded | v1.6 is a primitive/bridge architecture milestone |
| Broad RTX/GPU speedup | excluded | each claim requires exact-subpath evidence and review |
| App-free native internals | excluded | app-shaped compatibility/proof native paths remain |
| Vulkan/HIPRT/Apple RT active targets | excluded | frozen/proof surfaces before v2.1 |

## Backend Boundary

- Active v1.6 closure backends: Embree and OptiX.
- Embree remains the CPU RT fallback and same-contract comparison baseline.
- OptiX remains the NVIDIA runtime path for the validated native primitive
  subpaths.
- `--backend optix` is not by itself a public NVIDIA RT-core speedup claim.
- Vulkan, HIPRT, and Apple RT are preserved proof/frozen surfaces, not active
  v1.6 implementation targets.

## Validation Evidence

| Gate | Result | Evidence |
| --- | --- | --- |
| Windows source-tree slice | pass, 38 tests | `docs/reports/goal1605_windows_release_slice_cmd_2026-05-09.txt` |
| Linux source-tree slice | pass, 38 tests | `docs/reports/goal1605_linux_release_slice_clean_2026-05-09.txt` |
| Linux NVIDIA OptiX slice | pass, 33 tests | `docs/reports/goal1605_linux_nvidia_optix_slice_clean_2026-05-09.txt` |
| Public-docs overclaim audit | pass | Goal 1602 |
| Stable native-path app-leakage audit | pass with bounded claim | Goal 1603 |
| Blocked-claim regression | pass | Goal 1604 |

Validated commit for the Goal 1605 transcripts:

```text
ae92aa8eabc969da856ea730c7b82e19345ca3a3
```

## Known Issues

- Windows native Embree builds emit `dllexport` redeclaration warnings and a
  `getenv` deprecation warning. They did not fail the v1.6 validation slice.
- Full Windows unittest discovery hit the local 10-minute timeout while
  compiling native Embree code. The scoped release slice is the accepted Windows
  validation evidence for this package.
- Native internals are not fully app-agnostic; app-shaped compatibility/proof
  entry points remain and are excluded from the stable public primitive claim.
