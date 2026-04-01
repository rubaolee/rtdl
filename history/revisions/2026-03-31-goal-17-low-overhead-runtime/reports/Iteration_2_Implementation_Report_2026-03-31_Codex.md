## Goal 17 Implementation Report

Implemented first slice:

- packed native-ready input containers
  - `pack_segments(...)`
  - `pack_points(...)`
  - `pack_polygons(...)`
- prepared execution API
  - `prepare_embree(kernel)`
  - `PreparedEmbreeKernel`
  - `PreparedEmbreeExecution`
- thin native result view
  - `EmbreeRowView`

Current supported prepared workloads:

- `lsi`
- `pip`

Key architectural finding:

- packed inputs alone did not materially improve the ordinary dict-return `lsi` path
- packed inputs plus the raw-row view did materially reduce overhead for both `lsi` and `pip`

Current measured comparison from `scripts/goal17_compare_prepared_embree.py`:

### LSI

- current RTDL Embree total: `0.019190500024706125`
- prepared dict hot median: `0.022453541168943048`
- prepared raw hot median: `0.0006032912060618401`
- speedup vs current RTDL Embree using raw view: about `31.81x`
- raw gap vs Goal 15 native lower-bound path: about `0.58x`

### PIP

- current RTDL Embree total: `0.016894791973754764`
- prepared dict hot median: `0.015712832799181342`
- prepared raw hot median: `0.0003287079744040966`
- speedup vs current RTDL Embree using raw view: about `51.40x`
- raw gap vs Goal 15 native lower-bound path: about `0.79x`

Validation:

- `PYTHONPATH=src:. python3 -m unittest tests.goal17_prepared_runtime_test`
  - passed
- `PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py'`
  - `Ran 74 tests ... OK`
- `PYTHONPATH=src:. python3 scripts/goal17_compare_prepared_embree.py`
  - passed and produced comparison JSON

Interpretation:

- Goal 17 first slice is successful as an architecture proof:
  - the Python DSL can remain
  - a lower-overhead runtime path can materially close the native gap
- Goal 17 first slice does not prove that the normal dictionary-return RTDL path is now close to native
- the main remaining performance issue is still Python materialization on the result side
