# Goal4990 - Prepared/Query-Many Binary Operator Repeat Protocol

Date: 2026-07-04

## Objective

After Goal4988 removed the LSI pair-id device-column to NumPy round trip, attack the next ambiguity in the RayJoin Section 5.7 writer-free binary route:

- Is the remaining large cost an unavoidable per-query cost?
- Or is much of it first-use setup / first real working-set warmup that belongs to a prepared/query-many product route?

This goal does **not** change RTDL core semantics, does **not** add a RayJoin-specific core primitive, and does **not** authorize a fresh one-shot performance headline. It makes the prepared/query-many route measurable and auditable.

## Code Change

File changed:

- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`

Added a first-class repeat protocol:

```bash
--warmup-runs N
--repeat M
```

Default behavior is unchanged:

- `--repeat 1 --warmup-runs 0` returns the original single-run summary.

Repeat mode returns:

- `schema = rtdl.paper_reproduction.rayjoin.section57.binary_repeat_protocol.v1`
- explicit warmup rows
- measured rows
- median/best/worst writer-free hot time
- median LSI phase
- median downstream floor
- structural consistency checks
- claim boundary forbidding fresh one-shot or warm-only headlines

The measured protocol is same-process prepared/query-many:

```text
warmup rows: reported but excluded from median
measured rows: included in median
fresh one-shot headline: false
warm-only headline authorized: false
author comparison authorized: false
```

## Local Validation

Commands:

```bash
py -m py_compile Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
PYTHONPATH=src py -m unittest \
  tests.goal4990_binary_repeat_protocol_test \
  tests.goal4988_lsi_device_columns_direct_numba_handoff_test
```

Result:

```text
Ran 6 tests
OK
```

Added test:

- `tests/goal4990_binary_repeat_protocol_test.py`

The test verifies:

- CLI exposes `--repeat` and `--warmup-runs`.
- repeat summary keeps warmup rows visible.
- repeat summary blocks fresh one-shot and warm-only headlines.
- structural consistency is recorded.

## POD Runtime Evidence

POD:

```text
root@157.157.221.29 -p 25248
GPU: NVIDIA RTX 4000 Ada Generation
```

Command:

```bash
PYTHONPATH=src:. \
RTDL_OPTIX_LIB=/root/rtdl_goal4988/build/librtdl_optix.so \
RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR=/root/rtdl_goal4988/Paper-reproduction-apps/rayjoin-paper/_runs/public_sample/cache \
.venv/bin/python Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py \
  --left Paper-reproduction-apps/rayjoin-paper/_data/public_sample/br_county_clean_25_odyssey_final.txt \
  --right Paper-reproduction-apps/rayjoin-paper/_data/public_sample/br_soil_ascii_odyssey_final.txt \
  --pair-name br_county_soil \
  --device-columnar \
  --bounded-exact-lsi-device-columns \
  --bounded-exact-lsi-capacity 1000000 \
  --point-location-device-face-columns \
  --fast-scaled-point-pack \
  --compiled-group \
  --warmup-runs 1 \
  --repeat 3 \
  --summary Paper-reproduction-apps/rayjoin-paper/_runs/public_sample/rtdl/goal4990_repeat_protocol_public_sample.json
```

Artifact copied to:

```text
history/internal_docs/goal4990_pod_artifacts_2026-07-04/goal4990_repeat_protocol_public_sample.json
```

## POD Result

Warmup row, reported but excluded:

| Row | writer_free_hot_sec | LSI phase | downstream floor | carrier |
| --- | ---: | ---: | ---: | ---: |
| warmup 1 | 1.645118 | 0.868681 | 0.776437 | 0.717769 |

Measured rows:

| Row | writer_free_hot_sec | LSI phase | downstream floor | carrier |
| --- | ---: | ---: | ---: | ---: |
| measured 1 | 0.122847 | 0.063554 | 0.059293 | 0.005283 |
| measured 2 | 0.100514 | 0.045631 | 0.054884 | 0.005775 |
| measured 3 | 0.128475 | 0.068475 | 0.060000 | 0.005658 |

Median:

```text
median_writer_free_hot_sec = 0.12284692749381065
median_lsi_phase_sec       = 0.06355392746627331
median_downstream_floor_sec= 0.059293000027537346
best_writer_free_hot_sec   = 0.10051419585943222
```

Structural consistency:

```text
single_lsi_row_count = true
lsi_row_count = 20860
single_descriptor_pair_count = true
descriptor_pair_count = 28815
```

Device-column handoff stayed active:

```text
bounded_exact_lsi_numba_direct_handoff_used = true
lsi_pair_input_device_resident = true
lsi_pair_host_to_device_copy_used = false
```

## Interpretation

This result changes the performance picture, but only under the correct boundary.

What it proves:

- The writer-free binary route has a real same-process prepared/query-many mode.
- After one reported warmup run, the public County x Soil binary operator route runs around `0.10-0.13s`.
- The earlier large carrier cost is not a steady-state algorithm floor for this route:
  - warmup carrier: `0.717769s`
  - measured carrier: about `0.005-0.006s`
- LSI producer setup also drops substantially in the prepared same-process route:
  - warmup LSI: `0.868681s`
  - measured median LSI: `0.063554s`

What it does not prove:

- It does not replace the fresh one-shot number.
- It does not authorize a warm-only headline.
- It does not prove paper text output performance.
- It does not prove author-performance parity.
- It does not prove the same prepared behavior on top4 County x Zipcode.
- It does not eliminate the need to keep fresh and prepared/query-many columns side by side.

## Engineering Meaning

The result supports a concrete product distinction:

1. **Fresh one-shot overlay**
   - Includes first setup / first working-set costs.
   - Remains the conservative number for single-use reproduction runs.

2. **Prepared/query-many binary overlay operator**
   - Keeps RTDL/OptiX/Numba state in one process.
   - Runs repeated binary overlay queries with the same route and prepared state.
   - This is the relevant shape for a database/operator pipeline, where binary outputs feed downstream operators and text writer is not part of the hot path.

Goal4990 therefore does not merely "hide" cost. It makes the amortization boundary explicit and auditable.

## Claim Boundary

Allowed:

- "The Section 5.7 writer-free binary route now has an auditable prepared/query-many repeat protocol."
- "On the public County x Soil sample, after one reported warmup run, measured same-process writer-free binary runs have median `0.123s`."
- "The result preserves structural counts and keeps LSI pair-id input device-resident for the Numba reprojection handoff."

Not allowed:

- "v2.14.3 one-shot overlay is `0.123s`."
- "RTDL matches or beats the author implementation."
- "The paper text route is fast."
- "All RayJoin performance issues are solved."
- "This proves full device-resident end-to-end overlay with no remaining host boundaries."

## Next Work

1. Repeat the same protocol on the larger top4 County x Zipcode representative input.
2. Keep a side-by-side matrix:
   - fresh one-shot
   - prepared/query-many warmup row
   - prepared/query-many measured median
3. If top4 shows the same collapse, promote prepared/query-many binary overlay as the v2.14.3 performance route, while keeping fresh one-shot as a separate column.
4. If top4 does not collapse, decompose the top4-specific bottleneck before any further optimization.

## Exit Label

```text
completed_prepared_query_many_binary_operator_repeat_protocol_public_sample
```
