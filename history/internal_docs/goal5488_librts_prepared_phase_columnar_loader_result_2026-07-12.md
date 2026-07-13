# Goal5488: LibRTS Columnar Prepared-Phase Loader Probe

Date: 2026-07-12

Status: `implemented__POD_dtl_and_lakes_matched__review_pending`

## Objective

Exercise the Goal5487 generic `Aabb2DColumns` front door in the LibRTS
prepared point-contains app on exact official inputs. The purpose is to
separate the old Python row/ctypes packing cost from WKT text parsing and the
prepared query phase.

This is an app integration and phase diagnostic. It does not authorize a
LibRTS performance ratio or a Figure-6 claim.

## App Change

The app-owned loader now has a columnar route:

```text
WKT line -> MBR scalar lists -> Aabb2DColumns
         -> prepare_aabb_index_2d_columns -> prepared.count
```

The author wrapper, exact archive validation, input hashes, count comparator,
and phase fields are unchanged. The new route uses the generic system API and
does not add LibRTS semantics to RTDL core.

## POD Evidence

Both runs used the replacement RTX 4000 Ada POD, the same official archive
members, the same pinned author binary, and the same `point_contains` query
file. Both returned the exact author count.

| Case | Route | Author count | WKT load s | Prepare s | Prepared query wall s | Native primitive s |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `dtl_cnty` | Goal5486 row-shaped | 136,475 | 28.411 | 0.632 | 0.376 | 0.213 |
| `dtl_cnty` | Goal5488 columnar | 136,475 | 28.230 | 0.440 | 0.379 | 0.208 |
| `lakes.bz2` | Goal5486 row-shaped | 103,189 | 404.471 | 66.311 | 0.179 | 0.046 |
| `lakes.bz2` | Goal5488 columnar | 103,189 | 405.985 | 0.856 | 1.462 | 1.295 |

The columnar result artifacts are:

```text
Paper-reproduction-apps/librts-paper/results/librts_goal5488_dtl_cnty_prepared_phase_columns.json
Paper-reproduction-apps/librts-paper/results/librts_goal5488_lakes_bz2_prepared_phase_columns.json
```

## Interpretation

The large-input result is strong evidence that the old `66.311s` prepare phase
was dominated by host-side Python/ctypes packing: the aligned columnar ABI path
does not pay that per-row construction cost. WKT parsing is a separate floor
and remains about 405 seconds for `lakes.bz2`; Goal5487 did not solve it.

The new `lakes.bz2` prepared query wall is higher in this single run because
the route was run in a fresh process and first-use native pipeline state is not
controlled against the earlier sequential six-case matrix. It must not be
presented as a regression or a speedup until repeated same-process/clean-process
measurements are collected. The result proves count parity and phase separation,
not end-to-end performance parity.

## Claim Boundary

Authorized:

- exact same-input count agreement on `dtl_cnty` and `lakes.bz2`;
- use of the generic columnar AABB front door by the app;
- evidence that the old prepare phase included avoidable host packing work;
- separate WKT load, prepare, prepared query, and native primitive fields.

Not authorized:

- author-vs-RTDL performance ratio;
- end-to-end speedup headline;
- device zero-copy or device-resident index construction;
- Figure-6 reproduction, pair-row equality, or full-paper reproduction;
- Embree comparison.

## Verification

Focused local coverage now passes 12 tests across Goals5485-5488. The POD
columnar gate confirms both routes report `rt_core_accelerated=true` and the
same result counts. External review remains pending.
