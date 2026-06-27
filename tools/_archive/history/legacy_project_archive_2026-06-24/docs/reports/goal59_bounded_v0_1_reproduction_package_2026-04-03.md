# Goal 59 Bounded v0.1 Reproduction Package

Date: 2026-04-03

## Result

Goal 59 consolidates the strongest currently accepted bounded v0.1 reproduction
package into one explicit status document.

For the first two package families in this report, the accepted four-system
rows come directly from the accepted Goal 50 artifact, not from any later
consolidation note.

This package is accepted as:

- bounded
- host-validated on `192.168.1.20`
- correctness-closed on the listed packages
- performance-documented on the listed packages

This package is not accepted as:

- a full RayJoin-paper-identical reproduction
- nationwide closure
- closure of every lakes/parks continent family
- promotion of Vulkan beyond provisional status

## Accepted Systems

- PostGIS
- native C oracle
- Embree
- OptiX

## Accepted Bounded Packages

### 1. County ⊲⊳ Zipcode `top4_tx_ca_ny_pa`

Accepted workloads:

- `lsi`
- `pip`

Accepted closure:

- PostGIS == native C oracle == Embree == OptiX

Performance summary:

#### `lsi`

| System | Time (s) | Rows |
|---|---:|---:|
| PostGIS | `34.032305237` | `107513` |
| native C oracle | `89.336466250` | `107513` |
| Embree | `80.270740817` | `107513` |
| OptiX | `53.290038755` | `107513` |

#### `pip`

| System | Time (s) | Full-Matrix Rows | Positive Hits |
|---|---:|---:|---:|
| PostGIS | `0.430007831` | `16352128` | `7817` |
| native C oracle | `24.416985234` | `16352128` | `7817` |
| Embree | `16.812840088` | `16352128` | `7817` |
| OptiX | `19.255055544` | `16352128` | `7817` |

Boundary:

- PostGIS `pip` is measured as an indexed positive-hit query, then expanded into
  RTDL-equivalent full-matrix truth for parity

### 2. BlockGroup ⊲⊳ WaterBodies `county2300_s10`

Accepted workloads:

- `lsi`
- `pip`

Accepted closure:

- PostGIS == native C oracle == Embree == OptiX

Performance summary:

#### `lsi`

| System | Time (s) | Rows |
|---|---:|---:|
| PostGIS | `0.231961607` | `216` |
| native C oracle | `0.228627974` | `216` |
| Embree | `0.222838373` | `216` |
| OptiX | `0.893340557` | `216` |

#### `pip`

| System | Time (s) | Full-Matrix Rows | Positive Hits |
|---|---:|---:|---:|
| PostGIS | `0.008412973` | `71176` | `197` |
| native C oracle | `0.149648431` | `71176` | `197` |
| Embree | `0.117168097` | `71176` | `197` |
| OptiX | `0.647711122` | `71176` | `197` |

Boundary:

- same `pip` fairness boundary as County ⊲⊳ Zipcode:
  indexed PostGIS positive-hit query plus RTDL-equivalent truth expansion

### 3. LKAU ⊲⊳ PKAU `sunshine_tiny`

Accepted workloads:

- `lsi`
- `pip`

Accepted closure:

- PostGIS == native C oracle == Embree == OptiX

Performance summary:

#### `lsi`

| System | Time (s) | Rows |
|---|---:|---:|
| PostGIS | `0.062259014` | `15` |
| native C oracle | `1.913779297` | `15` |
| Embree | `2.128556676` | `15` |
| OptiX | `0.507164195` | `15` |

#### `pip`

| System | Time (s) | Rows | Positive Hits |
|---|---:|---:|---:|
| PostGIS | `0.004059802` | `73920` | `22` |
| native C oracle | `0.091486801` | `73920` | `22` |
| Embree | `0.057067710` | `73920` | `22` |
| OptiX | `0.384443247` | `73920` | `22` |

Boundary:

- this is a bounded Australia analogue from live OSM `way` geometry
- it is not continent-scale Australia-family closure
- it is not exact-input Dryad or SpatialHadoop reproduction

### 4. LKAU ⊲⊳ PKAU `overlay-seed analogue`

Accepted workload:

- `overlay-seed`

Accepted closure:

- PostGIS == native C oracle == Embree == OptiX

Performance summary:

| System | Time (s) | Rows |
|---|---:|---:|
| PostGIS | `0.228491376` | `73920` |
| native C oracle | `5.144722894` | `73920` |
| Embree | `0.085036251` | `73920` |
| OptiX | `0.567442065` | `73920` |

Boundary:

- this compares RTDL’s current `overlay-seed` row schema:
  - `left_polygon_id`
  - `right_polygon_id`
  - `requires_lsi`
  - `requires_pip`
- it is not full polygon overlay materialization
- the accepted OptiX result was observed on the GEOS-enabled build validated on
  `192.168.1.20`

## What Is Closed For v0.1

The accepted bounded v0.1 package now establishes:

- a trusted DSL/runtime/oracle foundation
- cross-system bounded correctness closure on:
  - two accepted exact-source family packages
  - one accepted bounded lakes/parks analogue
  - one accepted bounded `overlay-seed` analogue
- four-system parity where applicable:
  - PostGIS
  - native C oracle
  - Embree
  - OptiX
- indexed PostGIS external validation on the accepted bounded packages

## What Remains Deferred Or Incomplete

Deferred because the blocker is external acquisition instability, not backend
correctness:

- `LKAF ⊲⊳ PKAF`
- the other unstaged lakes/parks continent families

Still incomplete for a stronger final RayJoin-style repetition claim:

- additional bounded family closures beyond the accepted packages above
- any claim of nationwide or paper-identical matrix closure
- any claim that PostGIS and RTDL are performance-equivalent systems

## Still Provisional

- Vulkan remains provisional
- Vulkan has useful validation and tests, but it is not part of the accepted
  bounded v0.1 reproduction package

## Interpretation

The strongest honest project statement now is:

- RTDL has a bounded accepted reproduction package for the current v0.1 target
- that package is externally checked against PostGIS and internally consistent
  across the native C oracle, Embree, and OptiX
- the project is no longer in bring-up mode for those accepted packages
- the remaining gaps are matrix expansion and external-data availability, not
  foundation trustworthiness

## Source Reports

- [goal50_postgis_ground_truth_2026-04-02.md](goal50_postgis_ground_truth_2026-04-02.md)
- [goal54_lkau_pkau_four_system_2026-04-03.md](goal54_lkau_pkau_four_system_2026-04-03.md)
- [goal56_overlay_four_system_closure_2026-04-03.md](goal56_overlay_four_system_closure_2026-04-03.md)
