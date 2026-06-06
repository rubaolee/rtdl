# Goal3601 LibRTS Same-Contract Resident Repeat

Date: 2026-06-06

## Purpose

Goal3536 already stretched the LibRTS AABB row to the 10-second target, but the v2.3 app entrypoint did not expose the same resident-repeat CLI that current main now has. Goal3601 removes that ambiguity by using one neutral same-contract harness for both source trees:

- prepare one generic OptiX `AABB_INDEX_QUERY_2D` scene;
- prepare point and box query buffers once;
- run the same `count_prepared_queries` hot loop for `point_contains`, `range_contains`, and `range_intersects`;
- compare against each source tree's CPU oracle counts;
- record clean source commits and git status for both lanes.

This is internal v2.9 performance-triage evidence only.

Artifact directory:

`docs/reports/goal3601_librts_same_contract_resident_repeat_a5000/`

## Setup

| Field | Value |
| --- | --- |
| GPU | NVIDIA RTX A5000, driver 580.126.09, 24564 MiB |
| v2.3 commit | `2a28365d0246d51f3e3322b546f8a68c58632db4` |
| current commit | `42fb464c88502f5c32bcee2c7be255ed17c3aa20` |
| v2.3 git status | clean |
| current git status | clean |
| boxes | 1024 |
| point queries | 512 |
| box queries | 512 |
| seed | 2025 |
| repeat | 15000 measured runs per operation |
| warmup | 20 runs per operation |

Harness:

`scripts/goal3601_librts_same_contract_resident_repeat.py`

## Results

| Metric | v2.3 | current v2.9 | current speedup |
| --- | ---: | ---: | ---: |
| summed median hot query sec | 0.000741243 | 0.000736922 | 1.005864x |
| total measured hot query sec | 11.152972 | 11.107873 | 1.004060x |
| CPU-oracle count match | yes | yes | n/a |
| RT-core path | yes | yes | n/a |

Per operation:

| Operation | v2.3 median sec | current median sec | current speedup |
| --- | ---: | ---: | ---: |
| `point_contains` | 0.000192245 | 0.000188336 | 1.020759x |
| `range_contains` | 0.000196655 | 0.000196461 | 1.000991x |
| `range_intersects` | 0.000352343 | 0.000352126 | 1.000616x |

Counts matched exactly in both lanes:

| Operation | Count |
| --- | ---: |
| `point_contains` | 21475 |
| `range_contains` | 14675 |
| `range_intersects` | 32531 |

## Interpretation

LibRTS is now a clean parity row, not a broken or silently partial row. The current v2.9 generic prepared AABB path is slightly faster than v2.3 on the same hot resident contract, but the improvement is only about 1.006x overall. The important conclusion is therefore not a public speedup claim. The useful conclusion is that this benchmark row has a reproducible app-level hot-loop evidence path and should not be treated as a major v2.9 performance blocker.

The next serious performance work should focus on rows where the contract still lacks a strong current-main evidence path or where the measured gap is material. LibRTS range-count queries are already near identical between v2.3 and current main.

## Boundaries

This goal does not authorize:

- release or tag action;
- public v2.9 speedup claims;
- LibRTS paper reproduction claims;
- broad RT-core speedup claims;
- whole-app acceleration claims;
- true zero-copy claims.

No app-specific native symbol or engine customization was added. The harness calls the existing generic OptiX `AABB_INDEX_QUERY_2D` prepared-count contract.

## Validation

Pod validation:

```text
v2.3 summed median hot query sec: 0.0007412433624267578
current summed median hot query sec: 0.000736922025680542
current speedup: 1.005864035265095
v2.3 total measured hot query sec: 11.152972243726254
current total measured hot query sec: 11.107872820459306
counts equal: true
```

Local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3601_librts_same_contract_resident_repeat_test
```
