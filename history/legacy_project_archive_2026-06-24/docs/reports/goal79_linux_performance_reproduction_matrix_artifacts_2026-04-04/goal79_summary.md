# Goal 79 Linux Performance Reproduction Matrix

Host label: `lestat-lx1`

This package aggregates the accepted Linux-measured performance surfaces currently available in the RTDL repo.

Important boundary:

- rows are grouped by timing boundary
- end-to-end, prepared-execution, and cached repeated-call numbers are not interchangeable
- skipped surfaces are listed explicitly below

## Included Rows

### county_zipcode / end_to_end

- workload: `positive_hit_pip`
- dataset label: `top4_tx_ca_ny_pa`
- PostGIS: `3.238477414 s`
- Embree: `12.668624839 s`
- OptiX: `15.652318004 s`
- parity: `embree=True, optix=True`
- row count: `39073`

### blockgroup_waterbodies / end_to_end

- workload: `positive_hit_pip`
- dataset label: `county2300_s10`
- PostGIS: `0.007254268 s`
- Embree: `0.070980010 s`
- OptiX: `0.069386854 s`
- parity: `embree=True, optix=True`
- row count: `197`

### county_zipcode / prepared_execution

- workload: `positive_hit_pip`
- dataset label: `top4_tx_ca_ny_pa`
- backend: `optix`
- backend best/worst: `2.642049846 / 2.652621304 s`
- PostGIS best/worst: `3.313063422 / 3.333370466 s`
- beats PostGIS all reruns: `True`
- parity all reruns: `True`
- row count: `39073`

### county_zipcode / prepared_execution

- workload: `positive_hit_pip`
- dataset label: `top4_tx_ca_ny_pa`
- backend: `embree`
- backend best/worst: `1.026593471 / 1.347775829 s`
- PostGIS best/worst: `3.148009729 / 3.203224316 s`
- beats PostGIS all reruns: `True`
- parity all reruns: `True`
- row count: `39073`

### county_zipcode_selected_cdb / cached_repeated_call

- workload: `positive_hit_pip`
- dataset label: `goal28d_selected_cdb_slice`
- backend: `optix`
- first raw-input run: `0.485947633 s`
- best repeated run: `0.000862041 s`
- PostGIS first / best repeated: `0.000527199 / 0.000350572 s`
- parity all reruns: `True`
- row count: `5`

### county_zipcode_selected_cdb / cached_repeated_call

- workload: `positive_hit_pip`
- dataset label: `goal28d_selected_cdb_slice`
- backend: `embree`
- first raw-input run: `2.464383211 s`
- best repeated run: `0.000774917 s`
- PostGIS first / best repeated: `0.000497615 / 0.000325370 s`
- parity all reruns: `True`
- row count: `5`

## Winners By Boundary

- PostGIS wins: `county_zipcode:end_to_end, blockgroup_waterbodies:end_to_end, county_zipcode_selected_cdb:cached_repeated_call, county_zipcode_selected_cdb:cached_repeated_call`
- Embree wins: `county_zipcode:prepared_execution`
- OptiX wins: `county_zipcode:prepared_execution`

## Skipped Surfaces

- `lakes_parks_continent_families`: dataset acquisition unavailable or unstable in current project environment
- `vulkan_performance_matrix`: explicitly out of scope for Goal 79; backend not performance-competitive
- `oracle_backends_performance`: oracles are correctness references, not performance targets
- `lsi_or_overlay_postgis_matrix`: current available comparison package is limited to positive-hit pip timing surfaces with explicit PostGIS contract
