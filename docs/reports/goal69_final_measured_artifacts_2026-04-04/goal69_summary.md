# Goal 69 PIP Positive-Hit Performance

Host label: `lestat-lx1`
Database: `rtdl_postgis`

- compares indexed PostGIS positive-hit `pip` against RTDL's explicit positive-hit PIP mode
- this goal does not replace the accepted full-matrix parity contract from Goal 50
- it measures the narrower query shape that most closely matches the PostGIS execution contract

## County/Zipcode `top4_tx_ca_ny_pa`

- load sec: `39.638083649`
- compared backends: `optix, embree`
- PostGIS query mode: `indexed GiST-assisted positive-hit join with separate load/query timing`
- PostGIS indexed plan: `True`
- positive-hit parity: `optix=True, embree=True`

### PIP Positive Hits

- PostGIS: `3.238477414 s`
- plan nodes: `Gather Merge, Index Scan, Nested Loop, Seq Scan, Sort`
- hit rows: `39073`

#### OPTIX

- time: `15.652318004 s`
- parity: `True`
- hit rows: `39073`

#### EMBREE

- time: `12.668624839 s`
- parity: `True`
- hit rows: `39073`

## BlockGroup/WaterBodies `county2300_s10`

- load sec: `0.244869326`
- compared backends: `optix, embree`
- PostGIS query mode: `indexed GiST-assisted positive-hit join with separate load/query timing`
- PostGIS indexed plan: `True`
- positive-hit parity: `optix=True, embree=True`

### PIP Positive Hits

- PostGIS: `0.007254268 s`
- plan nodes: `Index Scan, Nested Loop, Seq Scan, Sort`
- hit rows: `197`

#### OPTIX

- time: `0.069386854 s`
- parity: `True`
- hit rows: `197`

#### EMBREE

- time: `0.070980010 s`
- parity: `True`
- hit rows: `197`
