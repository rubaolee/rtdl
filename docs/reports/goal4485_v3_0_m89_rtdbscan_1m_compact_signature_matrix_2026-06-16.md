# Goal4485 / V3.0 M89 RT-DBSCAN 1M Compact-Signature Matrix

## Outcome

M89 extends the Goal4484 RT-DBSCAN compact-signature route matrix from 524,288
points to 1,048,576 points on the RTX 4000 Ada pod.

The result strengthens the M88 decision: explicit predicate direct-status CuPy
remains the fastest measured same-contract compact-signature route on all three
profiles and both timing boundaries. Grouped-stream Numba remains the
conservative reference/fallback path.

This is route-choice evidence, not public whole-app, paper-reproduction,
GPU-vs-CPU, or broad RT-core speedup wording.

## Evidence

Raw packet:
`docs/reports/goal4485_v3_0_m89_rtdbscan_1m_compact_signature_matrix_2026-06-16.json`

Line packet:
`docs/reports/goal4485_v3_0_m89_rtdbscan_1m_compact_signature_matrix_2026-06-16.jsonl`

Hardware: NVIDIA RTX 4000 Ada Generation, driver 550.127.08.

The packet contains 18 successful rows and zero errors.

## Correctness Gate

The 1M rows use a same-contract signature gate: grouped-stream Numba,
grouped-stream CuPy, and predicate direct-status must produce the same compact
cluster/core/noise signature for each dataset and protocol.

| Dataset | Points | Protocols | Result |
| --- | ---: | --- | --- |
| `clustered3d` | 1,048,576 | one-shot, warmed replay | signatures match |
| `road3d` | 1,048,576 | one-shot, warmed replay | signatures match |
| `ngsim_dense` | 1,048,576 | one-shot, warmed replay | signatures match |

## Performance Matrix

One-shot table uses `prepare + measured replay` seconds. Predicate direct-status
includes direct-status prepare and OptiX count-threshold prepare.

| Dataset | Grouped Numba | Grouped CuPy | Predicate Direct-Status | Best | Speedup vs Grouped Numba |
| --- | ---: | ---: | ---: | --- | ---: |
| `clustered3d` | 26.739s | 25.793s | 11.362s | predicate direct-status | 2.35x |
| `road3d` | 12.278s | 12.775s | 10.425s | predicate direct-status | 1.18x |
| `ngsim_dense` | 7.429s | 7.854s | 6.509s | predicate direct-status | 1.14x |

Warmed replay table uses measured replay seconds after one warmup. This is the
resident prepared-route boundary.

| Dataset | Grouped Numba | Grouped CuPy | Predicate Direct-Status | Best | Speedup vs Grouped Numba |
| --- | ---: | ---: | ---: | --- | ---: |
| `clustered3d` | 19.744s | 20.314s | 5.773s | predicate direct-status | 3.42x |
| `road3d` | 7.282s | 7.842s | 5.254s | predicate direct-status | 1.39x |
| `ngsim_dense` | 2.235s | 2.774s | 1.243s | predicate direct-status | 1.80x |

## Interpretation

The 1M matrix confirms the M88 mechanism at a larger scale. Grouped-stream routes
remain heavier in replay because they preserve a grouped union stream shape and
then derive the compact signature. Predicate direct-status uses RTDL's generic
count-threshold device columns plus CuPy predicate direct-status union to consume
a more compact status representation.

The effect is strongest on `clustered3d`, still positive on `road3d`, and
positive on dense `ngsim_dense` even though one-shot timing is prepare-bound. The
prepare split also remains visible: predicate one-shot rows spend about 2.17s to
2.32s preparing the OptiX count-threshold handle and about 0.76s to 1.01s
preparing direct-status state before replay begins.

## Boundary

M89 authorizes this internal guidance:

- Use predicate direct-status explicitly for measured 524k and 1M compact
  cluster-size/noise/core signature profiles.
- Keep grouped-stream Numba as the conservative same-contract fallback/reference
  path.
- Keep full Python rows explicit.
- Keep graph-only component signatures separate from full DBSCAN wording.
- Keep automatic output-mode, partner, route, factor, and border-policy selection
  blocked.
- Treat prepare-cost reduction as the next real RT-DBSCAN optimization target if
  one-shot latency matters.
