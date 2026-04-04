# Goal Prepared County Positive-Hit Report: Embree

Host label: `lestat-lx1`
Database: `rtdl_postgis`
Case: `county_zipcode`
Backend: `embree`

- boundary: execution-ready / prepacked
- timed section includes only prepared `.run()` and the PostGIS indexed query
- parity is checked against PostGIS positive-hit output

## Preparation

- prepare kernel sec: `0.045654697`
- pack points sec: `0.162488782`
- pack polygons sec: `11.025372127`
- bind sec: `0.000021329`

## PostGIS

- indexed plan: `True`
- plan nodes: `Gather Merge, Index Scan, Nested Loop, Seq Scan, Sort`
- row count: `39073`
- sha256: `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`

## Runs

### Run 1

- backend sec: `1.347775829`
- PostGIS sec: `3.203224316`
- parity vs PostGIS: `True`
- row count: `39073`
- sha256: `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`

### Run 2

- backend sec: `1.026593471`
- PostGIS sec: `3.148009729`
- parity vs PostGIS: `True`
- row count: `39073`
- sha256: `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`

## Outcome

- beats PostGIS on all reruns: `True`
- parity preserved on all reruns: `True`
