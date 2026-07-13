# Goal4954-B Writer-Free Binary Baseline Measurement

Date: 2026-07-04

Status: completed_pending_review

Parent:

- `history/internal_docs/goal4954a_binary_overlay_contract_and_measurement_plan_2026-07-04.md`
- Antigravity verdict: `approve_goal4954a_contract_measurement_plan_open_goal4954b`

Exit label requested:

`writer_free_measurement_ready_for_device_columnar_work`

## Purpose

Goal4954-B measures the RayJoin Section 5.7 public sample as a binary
intermediate operator rather than as a paper text-output workload.

This goal is measurement-only. It does not implement optimization, public API,
native/core changes, or Layer 4 fusion.

## Owner Invariant

The measurement preserves the owner invariant:

> RTDL is a generic spatial dataflow system. RayJoin is an app/stress test.

The script uses RayJoin app adaptation to map paper/CDB data into generic
binary rows. The RTDL core/runtime is not changed.

## POD And Build Environment

POD:

```text
ssh root@213.173.108.15 -p 14399
hostname: be9235afec1a
GPU: NVIDIA RTX 4000 Ada Generation, compute capability 8.9
CUDA: /usr/local/cuda
nvcc: /usr/local/cuda/bin/nvcc
```

RTDL source:

```text
/root/rtdl_goal4954
HEAD: 8cc0597b
```

OptiX setup:

```text
OptiX SDK source: https://github.com/NVIDIA/optix-sdk
OptiX SDK tag: v9.0.0
OptiX SDK commit: 083bffe2011019ca2b9078f53206ff9f0193b63a
RTDL native library: /root/rtdl_goal4954/build/librtdl_optix.so
Build command:
  CUDA_PREFIX=/usr/local/cuda \
  OPTIX_PREFIX=/root/vendor/optix-sdk-github \
  OPTIX_CUDA_ARCH=sm_89 \
  make build-optix
```

Note: an earlier attempt with OptiX SDK 9.1 headers failed with
`Unsupported ABI version` on the POD's driver. The v9.0.0 tag is compatible
with this driver environment and was used for the final measurements.

## Input Data

Public RayJoin County x Soil sample:

| Role | File | SHA-256 |
|---|---|---|
| poly1_county | `br_county_clean_25_odyssey_final.txt` | `cee9f41da48c6f072b0692843cc23804517e8928f46c6c84675fc9a3b1e5a0e7` |
| poly2_soil | `br_soil_ascii_odyssey_final.txt` | `525a6dda0e42c1ed63f30cd5ffe8e9283697f3c53076837a122ba098ad530d9f` |
| section57_answer | `br_countyXbr_soil_answer.txt` | `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e` |

Download/verify command:

```bash
PYTHONPATH=src:. python3 Paper-reproduction-apps/rayjoin-paper/scripts/fetch_public_sample.py \
  --data-dir Paper-reproduction-apps/rayjoin-paper/_data/public_sample
```

## Measurement Command

```bash
cd /root/rtdl_goal4954
mkdir -p _goal4954b
PYTHONPATH=src:. RTDL_OPTIX_LIB=/root/rtdl_goal4954/build/librtdl_optix.so \
python3 history/internal_docs/goal4954b_writer_free_binary_overlay_measure.py \
  --left Paper-reproduction-apps/rayjoin-paper/_data/public_sample/br_county_clean_25_odyssey_final.txt \
  --right Paper-reproduction-apps/rayjoin-paper/_data/public_sample/br_soil_ascii_odyssey_final.txt \
  --pair-name br_county_soil_public \
  --author-overlay-compute-sec 0.0421 \
  --summary _goal4954b/writer_free_binary_summary.json
```

Three runs were collected. Artifacts were copied back to:

```text
history/internal_docs/goal4954b_artifacts/writer_free_binary_summary_run1.json
history/internal_docs/goal4954b_artifacts/writer_free_binary_summary_run2.json
history/internal_docs/goal4954b_artifacts/writer_free_binary_summary_run3.json
```

## Route

Measured route:

```text
public planar-map LSI
-> intersection reprojection
-> sort by source side
-> public point-location/PIP
-> midpoint generation and midpoint PIP
-> app-owned binary grouped rows
-> descriptor_pair_count downstream consumer
```

Excluded from binary metric:

- paper text writer;
- output-chain text formatting;
- file hashing;
- AuthorOfficial text-output comparison.

Preserved as correctness context:

- same public sample and same repaired RTDL paper route;
- binary row construction follows the same app-level overlay state as the
  paper route, but does not write paper text.

## 3-Run Results

| Metric | Run 1 | Run 2 | Run 3 | Median |
|---|---:|---:|---:|---:|
| writer-free hot path (s) | 5.803034 | 5.266287 | 5.309487 | 5.309487 |
| ratio vs AuthorOfficial overlay compute | 137.84x | 125.09x | 126.12x | 126.12x |
| LSI rows (s) | 1.714731 | 1.183238 | 1.213490 | 1.213490 |
| reprojection (s) | 0.735707 | 0.743315 | 0.741140 | 0.741140 |
| sort total (s) | 0.833509 | 0.841240 | 0.836403 | 0.836403 |
| binary grouped row construction (s) | 1.754741 | 1.735398 | 1.748347 | 1.748347 |
| descriptor-pair downstream consumer (s) | 0.688223 | 0.688320 | 0.695852 | 0.688320 |

Run 1 has a slower LSI phase than runs 2/3, likely due to first-use/cold effects.
The median is used as the summary value.

## Binary Output And Consumer

Binary row summary:

```text
group_count: 64,459
point_row_count: 673,371
skipped_group_count: 1,756
```

Downstream `descriptor_pair_count` summary:

```text
unique descriptor pairs: 28,815
total consumed rows: 673,371
```

This proves the binary route can feed a downstream consumer without parsing the
paper text writer.

## Interpretation

Goal4954-B confirms Claude's Goal4953 warning:

> Removing the writer isolates the compute gap; it does not close it.

The writer-free binary route median hot path is still:

```text
5.309487 s / 0.0421 s = 126.12x slower than AuthorOfficial overlay compute
```

Therefore, the correct conclusion is not "RTDL wins once writer is removed."
The correct conclusion is:

> The writer was a misleading sink cost, but the binary/operator path still has
> large pre-fusion costs.

## Current Bottlenecks

Median phase ranking among measured writer-free components:

1. binary grouped row construction: `1.748s`
2. LSI rows: `1.213s`
3. sort total: `0.836s`
4. reprojection: `0.741s`
5. downstream descriptor-pair consumer: `0.688s`
6. prepared-hot vertex/midpoint PIP traversal: tiny relative to the above

The immediate pre-fusion targets are therefore not traversal callbacks. They
are:

- app-owned binary row construction;
- columnar/sort/reprojection path;
- generic downstream aggregation implementation;
- possibly LSI row production/transfer, if it remains high after warm controls.

Layer 4 remains out of scope for Goal4954.

## Generic-System Boundary

This measurement does not promote the RayJoin binary row builder to RTDL core.
It is app-owned measurement code.

For future RTDL-core progress, the same carrier/consumer must pass the
non-RayJoin proof required by Goal4954-A.

## Decision

Goal4954-B should close as:

`writer_free_measurement_ready_for_device_columnar_work`

Recommended next subgoal:

Goal4954-C should start from the evidence above, but should not blindly follow
the old assumption that reprojection/sort are the only targets. The measured
largest pre-fusion component is binary grouped row construction, followed by
LSI rows and then reprojection/sort.

Goal4954-C should therefore be reframed as:

```text
columnar pre-fusion prototype for the measured writer-free bottlenecks
```

with two mandatory parts:

1. columnar reprojection/sort prototype, as originally planned;
2. app-owned binary row construction split to distinguish:
   - generic grouped-row carrier work;
   - RayJoin app reconstruction work.

No Layer 4 fusion or native traversal callback work is authorized by this
result.
