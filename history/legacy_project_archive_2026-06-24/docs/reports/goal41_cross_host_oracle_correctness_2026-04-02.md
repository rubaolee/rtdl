# Goal 41 Cross-Host Oracle Correctness

Date: 2026-04-02

## What Was Tested

The new native C/C++ oracle introduced in Goal 40 was validated on:

- this Mac
- Linux host `192.168.1.20`

Two correctness modes were used:

### Small 3-way checks

For small authored/fixture cases, the following had to agree:

- Python oracle: `run_cpu_python_reference(...)`
- native C/C++ oracle: `run_cpu(...)`
- Embree backend: `run_embree(...)`

Covered workloads:

- `lsi`
- `pip`
- `overlay`
- `ray_tri_hitcount`
- `segment_polygon_hitcount`
- `point_nearest_segment`

### Larger checks

For larger cases, the required comparison was:

- native C/C++ oracle: `run_cpu(...)`
- Embree backend: `run_embree(...)`

Large cases used:

- Mac synthetic large cases
- Linux exact-source large cases already staged from earlier goals

## Small 3-Way Results

### This Mac

All six workloads matched:

- `python_eq_c = true`
- `c_eq_embree = true`
- `python_eq_embree = true`

Observed row counts:

- `lsi`: `4`
- `pip`: `3`
- `overlay`: `1`
- `ray_tri_hitcount`: `2`
- `segment_polygon_hitcount`: `10`
- `point_nearest_segment`: `3`

### Linux `192.168.1.20`

All six workloads matched there as well:

- `python_eq_c = true`
- `c_eq_embree = true`
- `python_eq_embree = true`

Observed row counts were identical to the Mac small sweep:

- `lsi`: `4`
- `pip`: `3`
- `overlay`: `1`
- `ray_tri_hitcount`: `2`
- `segment_polygon_hitcount`: `10`
- `point_nearest_segment`: `3`

## Larger C-Oracle vs Embree Results

### This Mac

Two synthetic larger cases were used.

#### Large synthetic `lsi`

- parity: `true`
- C oracle: `0.002813167 s`
- Embree: `0.004781125 s`
- row count: `0`

This case was intentionally selective so the correctness check exercised large inputs without exploding output volume.

#### Large synthetic `pip`

- parity: `true`
- C oracle: `0.338979459 s`
- Embree: `0.197785917 s`
- row count: `500000`

### Linux `192.168.1.20`

Two exact-source larger families were used.

#### `County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa`

- county features: `441`
- zipcode features: `7035`
- county chains: `1612`
- zipcode chains: `10144`
- county segments: `1705027`
- zipcode segments: `9982960`
- zipcode probe points: `10144`

`lsi`

- pair parity: `true`
- C oracle: `88.391632435 s`
- Embree: `82.733328274 s`
- row count: `107513`

`pip`

- row parity: `true`
- C oracle: `151.869952414 s`
- Embree: `158.767087551 s`
- row count: `16352128`

#### `BlockGroup ⊲⊳ WaterBodies` `county2300_s10`

- blockgroup features: `279`
- waterbodies features: `172`
- blockgroup chains: `287`
- waterbodies chains: `248`
- blockgroup segments: `49812`
- waterbodies segments: `9629`
- water probe points: `248`

`lsi`

- pair parity: `true`
- C oracle: `0.220522783 s`
- Embree: `0.198707218 s`
- row count: `216`

`pip`

- row parity: `true`
- C oracle: `0.213191115 s`
- Embree: `0.192549768 s`
- row count: `71176`

## Issue Found During The Run

The first Linux sweep exposed a real portability bug in the new native oracle:

- `rtdl_oracle.cpp` used `std::stable_sort`
- but did not include `<algorithm>`

This failed on Linux during native-oracle build.

That was fixed in:

- commit `61fdcb6`

After that fix, the Linux small and large correctness sweeps completed successfully.

## Conclusion

Goal 41 validates the native oracle at the two required levels:

1. **small cases**
   - Python oracle, C oracle, and Embree all match on both hosts
2. **larger cases**
   - C oracle and Embree match on both hosts

So the current project state is:

- the old Python oracle remains available as a regression reference
- the new native C/C++ oracle is functioning correctly on both Mac and Linux
- and the Embree backend remains parity-clean against that oracle for the tested larger workloads
