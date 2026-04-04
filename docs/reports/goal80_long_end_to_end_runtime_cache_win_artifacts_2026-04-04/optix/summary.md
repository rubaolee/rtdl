# Goal 77 Runtime Cache Measurement: Optix

Host label: `lestat-lx1`
Database: `rtdl_postgis`
Case: `county_zipcode`
Backend: `optix`

- boundary: raw-input repeated-call timing in one process
- timing includes runtime-owned normalization, cache lookup, bind reuse when available, and backend run
- parity is checked against PostGIS positive-hit output on every run

## PostGIS

- indexed plan: `True`
- plan nodes: `Index Scan, Nested Loop, Seq Scan, Sort`
- row count: `7863`
- sha256: `fcb4304f40339a75c85a3065927caf73a897925af00a0c94048fb9bec1f15b79`

## Runs

### Run 1

- backend sec: `1.443262336`
- PostGIS sec: `0.374158744`
- parity vs PostGIS: `True`
- row count: `7863`
- sha256: `fcb4304f40339a75c85a3065927caf73a897925af00a0c94048fb9bec1f15b79`

### Run 2

- backend sec: `0.146764501`
- PostGIS sec: `0.369906195`
- parity vs PostGIS: `True`
- row count: `7863`
- sha256: `fcb4304f40339a75c85a3065927caf73a897925af00a0c94048fb9bec1f15b79`

### Run 3

- backend sec: `0.142673727`
- PostGIS sec: `0.367889968`
- parity vs PostGIS: `True`
- row count: `7863`
- sha256: `fcb4304f40339a75c85a3065927caf73a897925af00a0c94048fb9bec1f15b79`

## Outcome

- first run sec: `1.443262336`
- best repeated run sec: `0.142673727`
- repeated run improved vs first: `True`
- parity preserved on all runs: `True`
