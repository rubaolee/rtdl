# Goal 85 Vulkan Prepared Exact-Source County Report

Host label: `lestat-lx1`
Database: `rtdl_postgis`
Case: `county_zipcode`
Backend: `vulkan`

- boundary: execution-ready / prepacked
- input source: exact-source top4 county/zipcode CDB package
- timed section includes only prepared `.run()` and the PostGIS indexed query
- parity is checked against PostGIS positive-hit output

## Preparation

- prepare kernel sec: `0.002398542`
- pack points sec: `0.009439731`
- pack polygons sec: `0.699302030`
- bind sec: `0.000024004`

## PostGIS

- indexed plan: `True`
- plan nodes: `Index Scan, Nested Loop, Seq Scan, Sort`
- row count: `7863`
- sha256: `fcb4304f40339a75c85a3065927caf73a897925af00a0c94048fb9bec1f15b79`

## Runs

### Run 1

- Vulkan sec: `0.858198020`
- PostGIS sec: `0.393232202`
- parity vs PostGIS: `True`
- row count: `7863`
- sha256: `fcb4304f40339a75c85a3065927caf73a897925af00a0c94048fb9bec1f15b79`

### Run 2

- Vulkan sec: `0.333589648`
- PostGIS sec: `0.400314831`
- parity vs PostGIS: `True`
- row count: `7863`
- sha256: `fcb4304f40339a75c85a3065927caf73a897925af00a0c94048fb9bec1f15b79`

## Outcome

- beats PostGIS on all reruns: `False`
- parity preserved on all reruns: `True`
