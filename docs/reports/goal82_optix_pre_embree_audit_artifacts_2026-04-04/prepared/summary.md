# Goal Prepared County Positive-Hit Report: Optix

Host label: `lestat-lx1`
Database: `rtdl_postgis`
Case: `county_zipcode`
Backend: `optix`

- boundary: execution-ready / prepacked
- timed section includes only prepared `.run()` and the PostGIS indexed query
- parity is checked against PostGIS positive-hit output

## Preparation

- prepare kernel sec: `0.005272626`
- pack points sec: `0.050456302`
- pack polygons sec: `5.253130936`
- bind sec: `0.000019462`

## PostGIS

- indexed plan: `True`
- plan nodes: `Gather Merge, Index Scan, Nested Loop, Seq Scan, Sort`
- row count: `39073`
- sha256: `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`

## Runs

### Run 1

- backend sec: `3.429287890`
- PostGIS sec: `3.139067540`
- parity vs PostGIS: `True`
- row count: `39073`
- sha256: `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`

### Run 2

- backend sec: `1.147425041`
- PostGIS sec: `3.142702609`
- parity vs PostGIS: `True`
- row count: `39073`
- sha256: `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`

## Outcome

- beats PostGIS on all reruns: `False`
- parity preserved on all reruns: `True`
