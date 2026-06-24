# RTDL v3.0 Final Closeout

Status: release closeout complete for `v3.0`.

Date: 2026-06-18

## Verdict

v3.0 is closed as the V3 source-tree major release. The release publishes the
current ten-app benchmark route closure, app-author route policy, and
source-tree diagnostics. It upgrades the project from the V2.x row-scoped
cleanup sequence to a coherent V3 programming surface.

The release is intentionally conservative: V3.0 is complete for the current
benchmark-app/current-route matrix, while embedding, SDK, generated bindings,
device-buffer execution, external stream ordering, zero-copy framework interop,
and device-callable fusion remain V4.0 work.

## Completed Release Work

| Step | Status | Output |
| ---: | --- | --- |
| 1 | done | `VERSION` is `v3.0`; `pyproject.toml` is `3.0.0`. |
| 2 | done | Front page and current docs point to the V3.0 source-tree surface. |
| 3 | done | V3.0 release packet exists under `docs/release_reports/v3_0/`. |
| 4 | done | Source-tree doctor expects the V3.0 release package and validates current source-tree surfaces without making embedding a V3 release criterion. |
| 5 | done | V3 current matrix remains the canonical completion validation surface. |
| 6 | done | Public wording boundaries block unsupported claims. |
| 7 | done | Tag procedure is recorded in `tag_preparation.md`. |

## Release-Ready Scope

| Area | Released stance |
| --- | --- |
| Ten benchmark apps | Closed current routes; no immediate pod target remains. |
| App-author guidance | Primitive-first, prepared where useful, partner-explicit when custom continuation is required. |
| V4 scope boundary | Embedding/C ABI/SDK/generated-binding/zero-copy/external-runtime work is excluded from V3.0 release claims. |
| Validation | `scripts/rtdl_source_tree_doctor.py --json` and `scripts/run_test_matrix.py --group v3_current`. |
| Public performance | Still row-scoped and artifact-bound; no broad performance slogan. |

## Blocked Broader Claims

| Claim | Reason |
| --- | --- |
| Stable packaged SDK | Existing C ABI artifacts are V4.0 preparatory evidence, not frozen installer evidence or V3.0 release criteria. |
| Generated bindings | Current examples are hand-written; generated packages are V4 work. |
| Device-buffer query execution | CUDA/DLPack-like descriptors are metadata today. |
| External CUDA stream ordering | No event/same-stream ordering proof for borrowed framework streams. |
| Public true-zero-copy | No public transfer-counter proof of end-to-end true zero-copy. |
| Paper reproduction or author superiority | Requires row-specific data, output-contract, timing, and external review packets. |
| Automatic partner selection | V3 route policy is explicit user/app choice. |

## Final Verification

Local Windows validation, 2026-06-18:

```text
PYTHONPATH=src;. py -3 scripts\rtdl_source_tree_doctor.py --json
result: ok=true, version=v3.0, required_failures=[]
notes: optional local warnings for cupy, numba, and OptiX library availability

PYTHONPATH=src;. py -3 scripts\run_test_matrix.py --group v3_current
result: ok=true, module_count=39, Ran 147 tests, OK

PYTHONPATH=src;. py -3 scripts\run_test_matrix.py --group v3_release
result: ok=true, module_count=2, Ran 12 tests, OK

PYTHONPATH=src;. py -3 scripts\run_test_matrix.py --group v4_prep
result: ok=true, module_count=65, Ran 206 tests, OK
```

The `v4_prep` matrix is preserved as an archived preparatory regression guard.
It does not certify embedding, C ABI, SDK, generated binding, zero-copy, or
external-runtime work as part of V3.0.

Documentation polish scans, 2026-06-18:

```text
current-v2 wording scan over current docs: no hits
V3 doctor packet stale C ABI wording scan: no hits
V3.0 embedding-scope drift scan: no hits
```

Optional pod replay commands, if a CUDA/OptiX pod is available:

```text
PYTHONPATH=src:. python3 scripts/rtdl_source_tree_doctor.py --json
PYTHONPATH=src:. python3 scripts/run_test_matrix.py --group v3_current
```

This closeout does not claim a fresh pod replay from the publication edit
session. V3.0 is a source-tree release bounded by the local validation above
and the referenced benchmark evidence packets.

## Transition Rule

After v3.0, new embedding, SDK, generated binding, device-buffer query,
external-stream, public true-zero-copy, OptiX/Embree C ABI execution, and
device-callable fusion work belongs to V4 unless a later release packet
explicitly reopens V3.0 scope.
