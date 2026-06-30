# Goal 102 Status: Full Honest RayJoin Reproduction

Date: 2026-04-05
Status: complete

## Current interpretation

The current RTDL repository already contains a substantial amount of accepted
RayJoin-facing evidence. Goal 102 does not start from zero. It starts from a
mixed state:

- some rows are already closed exactly enough to carry forward
- some rows are closed only as bounded analogues
- some rows remain unavailable because the datasets are unstable or absent

The task now is to convert that mixed state into one final honest package using
only:

- Embree
- OptiX

## Working row classification

Strict audit rule used for this package:

- `exact` means paper-identical dataset coverage
- under that rule, no current RTDL row qualifies as `exact`
- the strongest `county_zipcode` results remain accepted and important, but they
  are still `bounded_analogue` rows for Goal 102 purposes

### Table 3 style rows

| Row | Workload | Current RTDL status | Classification | Notes |
| --- | --- | --- | --- | --- |
| County ⊲⊳ Zipcode | `lsi`, `pip` | long exact-source `pip` plus bounded package | `bounded_analogue` | strongest current row, but still not paper-identical dataset coverage |
| Block ⊲⊳ Water | `lsi`, `pip` | closest stable family is `BlockGroup ⊲⊳ WaterBodies` | `bounded_analogue` | honest substitute, not paper-identical |
| LKAF ⊲⊳ PKAF | `lsi`, `pip` | unstable public acquisition | `unavailable` | not silently dropped |
| LKAS ⊲⊳ PKAS | `lsi`, `pip` | unstaged | `unavailable` | same |
| LKAU ⊲⊳ PKAU | `lsi`, `pip` | accepted bounded analogue | `bounded_analogue` | useful support row |
| LKEU ⊲⊳ PKEU | `lsi`, `pip` | unstaged | `unavailable` | same |
| LKNA ⊲⊳ PKNA | `lsi`, `pip` | unstaged | `unavailable` | same |
| LKSA ⊲⊳ PKSA | `lsi`, `pip` | unstaged | `unavailable` | same |

### Figure 13 style rows

| Row | Workload | Current RTDL status | Classification | Notes |
| --- | --- | --- | --- | --- |
| Uniform LSI query time | `lsi` | accepted synthetic scalability analogue | `bounded_analogue` | already closed as controlled study |
| Gaussian LSI query time | `lsi` | accepted synthetic scalability analogue | `bounded_analogue` | same |
| Uniform LSI throughput | `lsi` | accepted synthetic scalability analogue | `bounded_analogue` | same |
| Gaussian LSI throughput | `lsi` | accepted synthetic scalability analogue | `bounded_analogue` | same |

### Figure 14 style rows

| Row | Workload | Current RTDL status | Classification | Notes |
| --- | --- | --- | --- | --- |
| Uniform PIP query time | `pip` | accepted synthetic scalability analogue | `bounded_analogue` | already closed as controlled study |
| Gaussian PIP query time | `pip` | accepted synthetic scalability analogue | `bounded_analogue` | same |
| Uniform PIP throughput | `pip` | accepted synthetic scalability analogue | `bounded_analogue` | same |
| Gaussian PIP throughput | `pip` | accepted synthetic scalability analogue | `bounded_analogue` | same |

### Table 4 / Figure 15 style rows

| Row | Workload | Current RTDL status | Classification | Notes |
| --- | --- | --- | --- | --- |
| Overlay timing family | `overlay` | accepted overlay-seed analogue only | `bounded_analogue` | not full polygon overlay |
| Overlay speedup summary | `overlay` | accepted overlay-seed analogue summary | `bounded_analogue` | must stay labeled as analogue |

## Execution priority for Goal 102

The first pass should not rerun everything blindly.

Priority order:

1. freeze the final matrix and carry-forward rules
2. rerun only the strongest rows that matter most:
   - long exact-source `county_zipcode` positive-hit `pip`
   - Embree
   - OptiX
3. refresh the accepted bounded analogue rows only where a clean rerun is
   missing or stale
4. do not spend time chasing unavailable continent datasets unless a stable
   acquisition path appears immediately

## Likely final honest package shape

The likely final Goal 102 package will say:

- one flagship family:
  - long `county_zipcode` positive-hit `pip`
- strict Goal 102 classification for that family:
  - `bounded_analogue`
- several bounded but accepted support families:
  - `top4_tx_ca_ny_pa`
  - `county2300_s10`
  - bounded `LKAU ⊲⊳ PKAU`
  - overlay-seed analogue
- accepted scalability analogues for Figure 13 / Figure 14
- explicit unavailable continent rows

## Completed execution rows

1. carried forward the accepted exact-source flagship `county_zipcode`
   positive-hit `pip` anchors
2. added fresh bounded top4 support reruns for:
   - Embree prepared
   - Embree repeated raw-input
   - OptiX prepared
   - OptiX repeated raw-input
3. froze the strict final classification matrix
4. wrote the final machine-readable Goal 102 summary
