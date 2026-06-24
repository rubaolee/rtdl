# Goal Prepared County Positive-Hit Report: Vulkan

Host label: `lestat-lx1`
Database: `rtdl_postgis`
Case: `county_zipcode`
Backend: `vulkan`

- boundary: execution-ready / prepacked
- timed section includes only prepared `.run()` and the PostGIS indexed query
- parity is checked against PostGIS positive-hit output

## Preparation

- prepare kernel sec: `0.006754150`
- pack points sec: `0.162884293`
- pack polygons sec: `11.041934685`
- bind sec: `0.000029641`

## PostGIS

- indexed plan: `True`
- plan nodes: `Gather Merge, Index Scan, Nested Loop, Seq Scan, Sort`
- row count: `39073`
- sha256: `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`

## Runs

### Run 1

- backend sec: `112.553943594`
- PostGIS sec: `3.117402789`
- parity vs PostGIS: `True`
- row count: `39073`
- sha256: `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`

### Run 2

- backend sec: `110.787909571`
- PostGIS sec: `3.127666747`
- parity vs PostGIS: `True`
- row count: `39073`
- sha256: `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`

## Outcome

- beats PostGIS on all reruns: `False`
- parity preserved on all reruns: `True`
