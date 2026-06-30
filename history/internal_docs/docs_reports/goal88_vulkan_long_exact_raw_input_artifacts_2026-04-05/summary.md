# Goal 77 Runtime Cache Measurement: Vulkan

Host label: `lestat-lx1-goal88`
Database: `rtdl_postgis`
Case: `county_zipcode`
Backend: `vulkan`

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

- backend sec: `16.140240988`
- PostGIS sec: `3.125241542`
- parity vs PostGIS: `True`
- row count: `39073`
- sha256: `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`

### Run 2

- backend sec: `6.709643080`
- PostGIS sec: `3.088001120`
- parity vs PostGIS: `True`
- row count: `39073`
- sha256: `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`

### Run 3

- backend sec: `6.827988418`
- PostGIS sec: `3.124289108`
- parity vs PostGIS: `True`
- row count: `39073`
- sha256: `0d12ece5d88b770ed8dcd6846cd8d83a70c0ce0c75b4cd762843632e037186ec`

## Outcome

- first run sec: `16.140240988`
- best repeated run sec: `6.709643080`
- repeated run improved vs first: `True`
- parity preserved on all runs: `True`
