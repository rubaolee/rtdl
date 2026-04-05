# Goal 102 Summary

- strict classification rule used:
  - `exact` means paper-identical dataset coverage
- result:
  - no current RTDL row qualifies as `exact`
  - Goal 102 closes as a bounded but honest reproduction package

## Flagship row

- `county_zipcode`
- positive-hit `pip`
- classification:
  - `bounded_analogue`

Prepared exact-source anchors:

- OptiX:
  - `2.5369022019876866 s` vs PostGIS `3.39459279399307 s`
- Embree:
  - `1.7738651990002836 s` vs PostGIS `3.40269520500442 s`
- parity:
  - `true`

Repeated raw-input exact-source anchors:

- OptiX:
  - first `4.49759002099745 s`
  - best repeated `2.124993502991856 s`
- Embree:
  - first `1.959970190000604 s`
  - best repeated `1.0921905469949706 s`
- parity:
  - `true`

## Fresh bounded top4 support reruns

Row count:

- `7863`

Prepared:

- OptiX:
  - `0.18207618700398598 s`
  - `0.1791208380018361 s`
- Embree:
  - `0.1821604330034461 s`
  - `0.14840258299955167 s`
- parity:
  - `true`

Repeated raw-input:

- OptiX:
  - first `1.0346060559968464 s`
  - best repeated `0.17935199600469787 s`
- Embree:
  - first `0.20209797599818558 s`
  - best repeated `0.1451086979941465 s`
- parity:
  - `true`

## Explicit unavailable rows

- `LKAF ⊲⊳ PKAF`
- `LKAS ⊲⊳ PKAS`
- `LKEU ⊲⊳ PKEU`
- `LKNA ⊲⊳ PKNA`
- `LKSA ⊲⊳ PKSA`

## Other accepted bounded rows

- `BlockGroup ⊲⊳ WaterBodies`
- bounded `LKAU ⊲⊳ PKAU`
- Figure 13 LSI scalability analogues
- Figure 14 PIP scalability analogues
- overlay-seed analogue
