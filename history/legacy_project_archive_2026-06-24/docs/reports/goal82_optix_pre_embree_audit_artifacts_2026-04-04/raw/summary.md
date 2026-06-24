# Goal 82 OptiX Pre-Embree Audit Raw Summary: Optix

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

- backend sec: `3.573603315`
- PostGIS sec: `3.235889516`
- parity vs PostGIS: `True`
- row count: `39073`
- sha256: `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`

### Run 2

- backend sec: `1.151226476`
- PostGIS sec: `3.257689920`
- parity vs PostGIS: `True`
- row count: `39073`
- sha256: `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`

### Run 3

- backend sec: `1.090809764`
- PostGIS sec: `3.224879186`
- parity vs PostGIS: `True`
- row count: `39073`
- sha256: `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`

## Outcome

- first run sec: `3.573603315`
- best repeated run sec: `1.090809764`
- repeated run improved vs first: `True`
- parity preserved on all runs: `True`
