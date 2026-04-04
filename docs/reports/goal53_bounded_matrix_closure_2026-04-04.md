# Goal 53 Bounded Matrix Closure

## Result

Goal 53 closes the bounded four-system comparison matrix for the strongest currently accepted RTDL packages on `192.168.1.20`.

Compared systems:

- PostGIS
- C oracle
- Embree
- OptiX

Accepted packages:

- `County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa`
- `BlockGroup ⊲⊳ WaterBodies` `county2300_s10`

Accepted workloads:

- `lsi`
- `pip`

## Source Of Truth

This matrix is intentionally built from the accepted Goal 50 artifact set, not from mixed older rounds.

Primary source:

- [goal50_postgis_ground_truth_2026-04-02.md](goal50_postgis_ground_truth_2026-04-02.md)

Why:

- Goal 50 already contains the accepted four-system rows for both packages and both workloads
- using Goal 50 directly avoids cross-phase timing drift
- therefore no refresh rerun was required for Goal 53

## Matrix

### County ⊲⊳ Zipcode `top4_tx_ca_ny_pa`

#### `lsi`

| System | Time (s) | Row Count | Correct vs PostGIS |
|---|---:|---:|---|
| PostGIS | `34.032305237` | `107513` | source of truth |
| C oracle | `89.336466250` | `107513` | `true` |
| Embree | `80.270740817` | `107513` | `true` |
| OptiX | `53.290038755` | `107513` | `true` |

PostGIS plan:

- `uses_index = true`
- index names: `county_zipcode_left_segments_geom_idx`
- node types: `Gather Merge`, `Index Scan`, `Nested Loop`, `Seq Scan`, `Sort`

#### `pip`

| System | Time (s) | Full-Matrix Rows | Positive Hits | Correct vs PostGIS |
|---|---:|---:|---:|---|
| PostGIS | `0.430007831` | `16352128` | `7817` | source of truth |
| C oracle | `24.416985234` | `16352128` | `7817` | `true` |
| Embree | `16.812840088` | `16352128` | `7817` | `true` |
| OptiX | `19.255055544` | `16352128` | `7817` | `true` |

PostGIS plan:

- `uses_index = true`
- index names: `county_zipcode_points_geom_idx`
- node types: `Index Scan`, `Nested Loop`, `Seq Scan`, `Sort`

### BlockGroup ⊲⊳ WaterBodies `county2300_s10`

#### `lsi`

| System | Time (s) | Row Count | Correct vs PostGIS |
|---|---:|---:|---|
| PostGIS | `0.231961607` | `216` | source of truth |
| C oracle | `0.228627974` | `216` | `true` |
| Embree | `0.222838373` | `216` | `true` |
| OptiX | `0.893340557` | `216` | `true` |

PostGIS plan:

- `uses_index = true`
- index names: `blockgroup_waterbodies_right_segments_geom_idx`
- node types: `Index Scan`, `Nested Loop`, `Seq Scan`, `Sort`

#### `pip`

| System | Time (s) | Full-Matrix Rows | Positive Hits | Correct vs PostGIS |
|---|---:|---:|---:|---|
| PostGIS | `0.008412973` | `71176` | `197` | source of truth |
| C oracle | `0.149648431` | `71176` | `197` | `true` |
| Embree | `0.117168097` | `71176` | `197` | `true` |
| OptiX | `0.647711122` | `71176` | `197` | `true` |

PostGIS plan:

- `uses_index = true`
- index names: `blockgroup_waterbodies_polygons_geom_idx`
- node types: `Index Scan`, `Nested Loop`, `Seq Scan`, `Sort`

## Interpretation

### Correctness

For the accepted bounded packages, the four-system matrix is now clean:

- PostGIS == C oracle == Embree == OptiX

That is the strongest current bounded correctness statement available in the project.

### Performance

The matrix shows that system leadership depends on both workload and scale.

On `County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa`:

- OptiX is the fastest RTDL backend for `lsi`
- Embree is the fastest RTDL backend for `pip`
- PostGIS is much faster on `pip`, but that must be interpreted carefully because PostGIS is executing an indexed positive-hit query while RTDL emits full-matrix truth rows

On `BlockGroup ⊲⊳ WaterBodies` `county2300_s10`:

- Embree is the fastest RTDL backend for both `lsi` and `pip`
- OptiX is correct but slower on this smaller package

## Fairness Boundary

This matrix is honest only with these boundaries stated explicitly:

- PostGIS `pip` is measured as an indexed positive-hit query
- RTDL `pip` times include full-matrix truth emission
- parity is established by expanding PostGIS hits into the same full-matrix truth semantics
- therefore PostGIS and RTDL are not running identical internal algorithms even though they agree exactly on the accepted truth set

## What Goal 53 Closes

Goal 53 closes the bounded four-system comparison package for:

- two accepted real-data families
- two workloads
- one trusted Linux host

## What Goal 53 Does Not Close

Goal 53 does not claim:

- nationwide matrix closure
- full RayJoin-paper reproduction closure
- that PostGIS and RTDL are performance-equivalent systems
- that OptiX or Embree leadership generalizes beyond the accepted bounded packages
