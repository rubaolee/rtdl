# Goal 103 Summary

- strict classification rule used:
  - `exact` means paper-identical dataset coverage
- result:
  - no current Vulkan row qualifies as `exact`
  - Goal 103 closes as a bounded but honest Vulkan-only reproduction package

## Flagship row

- `county_zipcode`
- positive-hit `pip`
- classification:
  - `bounded_analogue`

Prepared exact-source:

- Vulkan:
  - `6.139390789991012 s`
  - `6.164127523996285 s`
- PostGIS:
  - `3.2591196079883957 s`
  - `3.0466118039912544 s`
- parity:
  - `true`

Repeated raw-input exact-source:

- Vulkan:
  - first `16.14024098799564 s`
  - best repeated `6.709643080001115 s`
- PostGIS:
  - about `3.0880011199915316 s` to `3.125241542002186 s`
- parity:
  - `true`

## Bounded support row

- `top4_tx_ca_ny_pa`
- `county_zipcode`
- prepared / prepacked boundary

Accepted result:

- row count `7863`
- parity `true`
- Vulkan:
  - `0.8581980200033286 s`
  - `0.3335896480057272 s`
- PostGIS:
  - `0.39323220199730713 s`
  - `0.4003148310002871 s`

## Hardware validation

- Goal 51 Vulkan ladder:
  - `8 / 8` parity-clean
- focused Vulkan unit/backend slice:
  - `20` tests
  - `OK`

## Explicit unavailable rows

- `County ⊲⊳ Zipcode` `lsi`
- `Block ⊲⊳ Water`
- `LKAU ⊲⊳ PKAU`
- continent `LK* ⊲⊳ PK*`
- Figure 13 Vulkan scalability package
- Figure 14 Vulkan scalability package
- Vulkan overlay analogue package

## Honest outcome

- Vulkan is real
- Vulkan is hardware-validated
- Vulkan is parity-clean on the accepted flagship row
- Vulkan remains slower than PostGIS on that long row
- the broader RayJoin paper matrix remains mostly unavailable for a Vulkan-only
  package
