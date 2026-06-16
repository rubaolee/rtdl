# Goal4444 / V3.0 M48 Triangle Numba Direct-Binary Summary

Status: `accept-with-boundary`

M48 fixes the largest unfairness in the triangle-counting Numba partner row.
M27 made the `--partner numba` front door executable, but it built the compact
RT-Graph summary contract through the old Python contract builder and then
uploaded summary columns to Numba device arrays. That made the Numba row mostly
a Python staging benchmark.

M48 replaces that staging path with:

```text
binary edge list -> vectorized NumPy CSR/two-hop summary -> Numba device arrays -> same RTDL/OptiX summary primitive
```

This is still not a fully device-side graph-construction primitive. It is a
cleaner no-C++ Python-source partner route that preserves the same engine
boundary: RTDL sees generic triangles, rays, weights, and scalar summaries; app
graph construction stays outside the native engine.

## Pod Evidence

Hardware: NVIDIA RTX 4000 Ada Generation, driver 550.127.08, 20 GB.

Artifacts:

```text
docs/reports/goal4444_v3_0_m48_triangle_partner_dual_cliques5000_2026-06-16.json
docs/reports/goal4444_v3_0_m48_triangle_partner_dual_cliques50000_2026-06-16.json
docs/reports/goal4444_v3_0_m48_triangle_partner_dual_cliques200000_2026-06-16.json
```

All rows passed oracle parity and per-mode CuPy/Numba signature matching.

## Performance Matrix

| Cliques | Mapping | Partner | Triangles | Total ms | Partner ms | Query median ms | M27 Numba total ms | Numba total speedup vs M27 |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 5,000 | RT-2A1 | CuPy | 20,000 | `44.059` | `25.684` | `0.384` | n/a | n/a |
| 5,000 | RT-2A1 | Numba | 20,000 | `20.249` | `12.548` | `0.369` | `219.420` | `10.84x` |
| 5,000 | RT-1A2 | CuPy | 20,000 | `14.257` | `7.916` | `0.365` | n/a | n/a |
| 5,000 | RT-1A2 | Numba | 20,000 | `21.818` | `12.139` | `0.822` | `215.188` | `9.86x` |
| 50,000 | RT-2A1 | CuPy | 200,000 | `84.295` | `52.908` | `1.871` | n/a | n/a |
| 50,000 | RT-2A1 | Numba | 200,000 | `110.756` | `88.480` | `1.091` | `1904.068` | `17.19x` |
| 50,000 | RT-1A2 | CuPy | 200,000 | `34.643` | `21.405` | `1.359` | n/a | n/a |
| 50,000 | RT-1A2 | Numba | 200,000 | `118.222` | `85.862` | `1.339` | `1951.729` | `16.51x` |
| 200,000 | RT-2A1 | CuPy | 800,000 | `140.671` | `106.681` | `1.971` | n/a | n/a |
| 200,000 | RT-2A1 | Numba | 800,000 | `352.764` | `300.714` | `1.959` | `8139.455` | `23.07x` |
| 200,000 | RT-1A2 | CuPy | 800,000 | `74.989` | `49.876` | `3.271` | n/a | n/a |
| 200,000 | RT-1A2 | Numba | 800,000 | `397.367` | `303.008` | `3.280` | `7932.472` | `19.96x` |

## Interpretation

M48 changes the fairness of the partner comparison:

- The old Numba row was dominated by Python graph-contract construction. At
  200,000 cliques it spent `7.54-7.81s` in partner construction.
- The new Numba row spends about `0.301-0.303s` in partner construction at the
  same scale.
- The RTDL/OptiX query medians remain small and comparable across partners:
  about `1.96ms` for RT-2A1 and `3.27-3.28ms` for RT-1A2 at 200,000 cliques.
- CuPy remains the large-scale performance route: at 200,000 cliques Numba is
  still `2.51x` slower on RT-2A1 total time and `5.30x` slower on RT-1A2 total
  time.

So the honest conclusion is not "Numba beats CuPy." The honest conclusion is:
the no-C++ Numba route is now a real same-contract reference instead of a
Python-staging artifact, and the remaining gap is graph-construction fusion and
Numba-side geometry construction.

## Boundary

Allowed wording:

> Goal4444 reduces triangle-counting Numba partner construction debt by roughly
> 25x at the 200,000-clique scale while preserving the same RTDL/OptiX summary
> primitive and oracle signatures. CuPy remains the current large-scale
> performance partner.

Forbidden wording:

- no full RT-Graph paper reproduction claim;
- no broad RT-core triangle-counting speedup claim;
- no claim that Numba is universally faster than CuPy;
- no automatic partner selection;
- no app-specific native RTDL engine logic.
