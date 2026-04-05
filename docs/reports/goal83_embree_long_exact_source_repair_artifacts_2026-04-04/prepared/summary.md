# Goal Prepared County Positive-Hit Report: Embree

Host label: `lx1`
Database: `rtdl_postgis`
Case: `county_zipcode`
Backend: `embree`

- boundary: execution-ready / prepacked
- timed section includes only prepared `.run()` and the PostGIS indexed query
- parity is checked against PostGIS positive-hit output

## Preparation

- prepare kernel sec: `0.033447078`
- pack points sec: `0.054710918`
- pack polygons sec: `5.230944873`
- bind sec: `0.000019789`

## PostGIS

- indexed plan: `True`
- plan nodes: `Gather Merge, Index Scan, Nested Loop, Seq Scan, Sort`
- row count: `39073`
- sha256: `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`

## Runs

### Run 1

- backend sec: `1.773865199`
- PostGIS sec: `3.402695205`
- parity vs PostGIS: `True`
- row count: `39073`
- sha256: `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`

## Outcome

- beats PostGIS on all reruns: `True`
- parity preserved on all reruns: `True`
