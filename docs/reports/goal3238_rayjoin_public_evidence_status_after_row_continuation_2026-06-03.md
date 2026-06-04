# Goal3238: RayJoin Public Evidence Status After Row Continuation

Date: 2026-06-03

## Position

RTDL now has bounded public-CDB evidence for both scalar/count and row
continuation across the current RayJoin workload families.

This is a meaningful step beyond fixture-only evidence:

- PIP has public positive-assignment count parity and public positive-hit row
  continuation parity.
- LSI has public segment-intersection count parity and public
  segment-intersection row continuation parity.
- Overlay has public active-count parity, public pair-dependency row parity,
  and larger bounded row-scale parity up to 233,766 rows.

The native engine remains generic. RayJoin-specific interpretation remains in
Python app code.

## Current Evidence Table

| Family | Evidence | Largest Public Case | Contract | Result |
| --- | --- | --- | --- | --- |
| PIP count | Goal3227 | `pip_county512` | `positive_assignment_count` | 1430/1430 |
| PIP rows | Goal3232 | `pip_county512` | positive point/shape membership rows normalized at app boundary | 1430 rows, symmetric difference 0 |
| LSI count | Goal3218 | `lsi_county256_soil256_count512` | segment-pair intersection count | 269/269 |
| LSI rows | Goal3232 | `lsi_county256_soil256_count512` | segment-pair intersection rows | 269 rows, symmetric difference 0, `max_lsi_coordinate_delta = 0` |
| Overlay count | Goal3225 | `overlay_county256_soil256` | active pair-dependency count | 9/9 |
| Overlay rows | Goal3232 | `overlay_county256_soil256` | pair-dependency rows with LSI/PIP flags | 56,876 rows, symmetric difference 0 |
| Overlay row scale | Goal3234 | `overlay_county512_soil512` | pair-dependency rows with LSI/PIP flags | 233,766 rows, symmetric difference 0 |

## Performance Reading

The row-continuation artifacts expose two timing layers:

- `prepared_query_sec`: the native prepared OptiX query phase.
- `prepared_total_seconds`: cold preparation plus host row materialization plus
  the app-level row-set validation path.

For overlay scale:

- `overlay_county384_soil384`: 130,320 rows, prepared query `0.060 s`, prepared
  total `1.154 s`, CPU reference validation `48.723 s`.
- `overlay_county512_soil512`: 233,766 rows, prepared query `0.085 s`, prepared
  total `0.392 s`, CPU reference validation `81.179 s`.

These are promising engineering signals, especially for row continuation, but
they are not yet public speedup claims because they are single-repeat, bounded
slice artifacts and not same-paper, same-system RayJoin comparisons.

## Remaining RayJoin Gaps

- Full paper-scale Brazil county/soil datasets are still not covered.
- Cross-system RTDL-vs-RayJoin execution on the same dataset and hardware is
  still open.
- Multi-repeat steady-state statistics for the row-continuation path are still
  open.
- Device-resident row-stream continuation is still future work; current
  validation materializes rows on the host.
- Broader GPU-family evidence is still open.
- True zero-copy, broad RT-core speedup, `RTDL beats RayJoin`, and paper
  reproduction claims remain unauthorized.

## Next Engineering Target

The next useful RayJoin engineering target is a same-contract comparison packet
against the RayJoin repository or a paper-closer equivalent harness:

1. Use the same public CDB slices already validated here.
2. Run RayJoin's own implementation, if buildable, on matching inputs.
3. Run RTDL prepared OptiX count and row modes on the same inputs.
4. Report exact contracts separately: count, row continuation, and overlay
   active-seed semantics.
5. Keep the same six false claim-boundary flags until the comparison is
   independently reviewed.

## Boundary

This report does not authorize release, public speedup claims, broad RT-core
claims, true zero-copy claims, `RTDL beats RayJoin` claims, or RayJoin
paper-reproduction claims. It is a planning/status packet for the next RayJoin
work.
Standard boundary phrase: no broad RT-core claims are authorized here.
Standard boundary phrase: no RayJoin paper-reproduction claims are authorized here.
