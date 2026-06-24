# Goal 81 OptiX Long Exact Raw-Input Win: Optix

Host label: `lestat-lx1`
Database: `rtdl_postgis`
Case: `county_zipcode`
Backend: `optix`

- boundary: raw-input repeated-call timing in one process
- timing includes runtime-owned normalization, cache lookup, bind reuse when available, and backend run
- parity is checked against PostGIS positive-hit output on every run

## PostGIS

- indexed plan: `True`
- plan nodes: `Gather Merge, Index Scan, Nested Loop, Seq Scan, Sort`
- row count: `39073`
- sha256: `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`

## Runs

### Run 1

- backend sec: `3.602868046`
- PostGIS sec: `3.133568043`
- parity vs PostGIS: `True`
- row count: `39073`
- sha256: `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`

### Run 2

- backend sec: `1.159974238`
- PostGIS sec: `3.121261025`
- parity vs PostGIS: `True`
- row count: `39073`
- sha256: `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`

### Run 3

- backend sec: `1.086635833`
- PostGIS sec: `3.148949364`
- parity vs PostGIS: `True`
- row count: `39073`
- sha256: `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`

## Outcome

- first run sec: `3.602868046`
- best repeated run sec: `1.086635833`
- repeated run improved vs first: `True`
- parity preserved on all runs: `True`
