# Goal 77 Runtime Cache Measurement: Embree

Host label: `lestat-lx1`
Database: `rtdl_postgis`
Case: `county_zipcode`
Backend: `embree`

- boundary: raw-input repeated-call timing in one process
- timing includes runtime-owned normalization, cache lookup, bind reuse when available, and backend run
- parity is checked against PostGIS positive-hit output on every run

## PostGIS

- indexed plan: `True`
- plan nodes: `Index Scan, Nested Loop, Seq Scan, Sort`
- row count: `5`
- sha256: `5594dc413a14e19790c7c2eb81c5d6163a293dd0825ee5e408f529744a7656fc`

## Runs

### Run 1

- backend sec: `2.464383211`
- PostGIS sec: `0.000497615`
- parity vs PostGIS: `True`
- row count: `5`
- sha256: `5594dc413a14e19790c7c2eb81c5d6163a293dd0825ee5e408f529744a7656fc`

### Run 2

- backend sec: `0.000887814`
- PostGIS sec: `0.000462333`
- parity vs PostGIS: `True`
- row count: `5`
- sha256: `5594dc413a14e19790c7c2eb81c5d6163a293dd0825ee5e408f529744a7656fc`

### Run 3

- backend sec: `0.000774917`
- PostGIS sec: `0.000325370`
- parity vs PostGIS: `True`
- row count: `5`
- sha256: `5594dc413a14e19790c7c2eb81c5d6163a293dd0825ee5e408f529744a7656fc`

## Outcome

- first run sec: `2.464383211`
- best repeated run sec: `0.000774917`
- repeated run improved vs first: `True`
- parity preserved on all runs: `True`
