# Goal 50 PostGIS Status

Date: 2026-04-03

Scope:
- Goal 50 remains in progress.
- This status report covers the fresh `county_zipcode top4_tx_ca_ny_pa` rerun on `192.168.1.20` after two RTDL `pip` fixes.
- The purpose is to freeze the current technical state before the next debugging step.

## What Is Now Correct

- PostGIS is installed and operational on `192.168.1.20`.
- The Goal 50 harness uses indexed SQL rather than brute-force joins.
- `lsi` is now parity-clean against PostGIS for all three RTDL backends on the accepted large county/zipcode package:
  - C oracle
  - Embree
  - OptiX

## Current County/Zipcode Result

Source summary:
- Remote file:
  - `/home/lestat/work/rtdl_goal50_run/build/goal50_final_v2/county_zipcode/goal50_summary.json`

Package:
- county features: `441`
- county chains: `1612`
- zipcode features: `7035`
- zipcode chains: `10144`
- derived points: `10144`
- derived polygons: `1612`

### LSI

- PostGIS query mode: indexed GiST-assisted join
- PostGIS time: `34.277083718 s`
- row count: `107513`
- parity:
  - CPU: `true`
  - Embree: `true`
  - OptiX: `true`

Backend times:
- CPU: `90.929071689 s`
- Embree: `82.449129710 s`
- OptiX: `52.795198332 s`

### PIP

- PostGIS query mode: indexed GiST-assisted positive-hit join via `&&` + `ST_Covers`
- PostGIS time: `0.433912105 s`
- expanded full-matrix row count: `16352128`
- PostGIS positive-hit count: `7817`

Backend times:
- CPU: `200.425307321 s`
- Embree: `191.676810692 s`
- OptiX: `81.791817020 s`

Parity:
- CPU: `false`
- Embree: `false`
- OptiX: `false`

Hashes:
- PostGIS full-matrix truth: `ba09aeeccfb76d4d635a38c8e4de39813131e0931fa9bb607fab07ad15288d43`
- CPU: `a5a167ce398596e0cd8d741a47d298ce1c9e1472dc89f848e3d498e212700d2c`
- Embree: `a5a167ce398596e0cd8d741a47d298ce1c9e1472dc89f848e3d498e212700d2c`
- OptiX: `ac57f361eba044df7a87b417cebb33b3d0f7faf5466afd3608d31ca9dc02eb3f`

## What Was Fixed During This Round

Two real RTDL `pip` bugs were found and fixed locally:

1. Degenerate closing-edge boundary bug
- Repeated closing vertices created zero-length edges.
- The old boundary check could classify arbitrary points as lying on those edges.

2. Short-edge boundary tolerance bug
- The old boundary check used a raw cross-product epsilon.
- On short segments, that produced an overly large effective point-to-segment tolerance.
- A concrete false-positive pair was reduced to:
  - point id `1`
  - polygon id `123`
- After the second fix, that exact pair now agrees with PostGIS:
  - RTDL: `False`
  - PostGIS: `False`

## Current Interpretation

The remaining Goal 50 blocker is now narrower:

- `lsi` is in good shape.
- `pip` is still not PostGIS-clean on `county_zipcode top4`.
- CPU and Embree now agree with each other on this package.
- OptiX still differs from the CPU/Embree hash on this package.

So the current likely structure is:

1. one remaining shared `pip` semantic mismatch between:
   - PostGIS
   - RTDL C oracle / Embree

2. one additional OptiX-side `pip` mismatch relative to the oracle

## Next Step

Do not publish Goal 50 yet.

Next debugging order:

1. isolate actual RTDL-positive / PostGIS-negative `pip` pairs from the fresh county/zipcode package
2. fix the remaining shared CPU/Embree `pip` semantic gap
3. then fix OptiX `pip` to match the oracle
4. rerun county/zipcode
5. only after county/zipcode is fully clean, run `blockgroup_waterbodies`
6. then perform Claude and Gemini review for final Goal 50 closure
