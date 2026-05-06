# Goal 1393 - v1.5 Stable Primitive Claim Evidence

Date: 2026-05-06

## Scope

This packet prepares exact-subpath evidence for the final v1.5 public-readiness path.

Stable primitive surface:

- `ANY_HIT`
- `COUNT_HITS`
- `REDUCE_FLOAT(MIN)`
- `REDUCE_FLOAT(MAX)`
- `REDUCE_FLOAT(SUM)`
- `REDUCE_INT(COUNT)`
- `REDUCE_INT(SUM)`

Boundaries:

- Active v1.5 engineering backends are Embree and OptiX.
- Vulkan, HIPRT, and Apple RT remain frozen before v2.1.
- `COLLECT_K_BOUNDED` remains experimental and is not promoted by this packet.
- This packet does not authorize public v1.5 release wording, public speedup wording, broad NVIDIA wording, package/install claims, or tag actions.

## Runner

Script:

```sh
scripts/goal1393_v1_5_stable_primitive_evidence_runner.py
```

The runner records:

- source commit and platform/tool versions,
- stable scalar reduction outputs and timings,
- direct `ANY_HIT` plus `COUNT_HITS` outputs and timings for requested backends,
- optional prepared OptiX `ANY_HIT` plus `COUNT_HITS` repeated-query timing,
- parity against CPU oracle where comparable,
- explicit non-public claim boundary.

## Local Smoke Validation

Command:

```sh
PYTHONPATH=src:. python3 scripts/goal1393_v1_5_stable_primitive_evidence_runner.py \
  --copies 8 \
  --direct-repeats 2 \
  --scalar-repeats 3 \
  --backend cpu \
  --skip-prepared \
  --output /tmp/goal1393_local.json
```

Result:

```text
source_commit: 6aa012da28cec9b9d43fa709dd3c70e452751e42
platform: Darwin arm64, Python 3.14.0
stable_primitives: ANY_HIT, COUNT_HITS, REDUCE_FLOAT(MIN), REDUCE_FLOAT(MAX), REDUCE_FLOAT(SUM), REDUCE_INT(COUNT), REDUCE_INT(SUM)
scalar_reductions: all status ok
direct_anyhit_count.cpu: status ok, row_count 16, hit_count 8
public_wording_authorized: false
```

## Fresh Git Pod Plan

Use a fresh Git checkout on the pod, then run:

```sh
OUTPUT_JSON=docs/reports/goal1393_v1_5_stable_primitive_pod_results/rtdl_pod_env.json \
OUTPUT_ENV=docs/reports/goal1393_v1_5_stable_primitive_pod_results/rtdl_pod_env.sh \
bash scripts/rtdl_pod_env_probe.sh

. docs/reports/goal1393_v1_5_stable_primitive_pod_results/rtdl_pod_env.sh
make build-embree
make build-optix

PYTHONPATH=src:. python3 scripts/goal1393_v1_5_stable_primitive_evidence_runner.py \
  --copies 256 \
  --direct-repeats 5 \
  --scalar-repeats 100 \
  --prepared-query-repeats 100 \
  --output docs/reports/goal1393_v1_5_stable_primitive_pod_results/stable_primitive_evidence.json
```

Acceptance requirements for public-readiness input:

- Environment probe is preserved.
- CPU oracle direct `ANY_HIT` plus `COUNT_HITS` succeeds.
- Scalar reduction cases for all stable `REDUCE_*` and `COUNT_HITS` primitives return expected values.
- Embree and OptiX statuses are recorded explicitly.
- Any successful Embree/OptiX result matches CPU hit count.
- Prepared OptiX status is recorded explicitly; if successful, its hit count matches CPU.
- The artifact still says `public_wording_authorized: false`.

## Fresh Git Pod Evidence

SSH target:

```text
root@213.173.108.215 -p 14800 -i ~/.ssh/id_ed25519_rtdl_codex
```

Fresh Git commit:

```text
c0b57ae274129aa536e6ae0069f188a138bbefc1
```

Environment summary:

```text
system: Linux x86_64
kernel: 6.8.0-49-generic
python: 3.12.3
os_id: ubuntu
package_manager: apt-get
cuda_prefix: /usr/local/cuda
nvcc: /usr/local/cuda/bin/nvcc
nvcc_exists: true
optix_prefix: /root/vendor/optix-dev
optix_header_exists: true
embree_version: 4.3.0
```

Build summary:

```text
make build-embree: passed
make build-optix: passed
```

Evidence command:

```sh
PYTHONPATH=src:. python3 scripts/goal1393_v1_5_stable_primitive_evidence_runner.py \
  --copies 256 \
  --direct-repeats 5 \
  --scalar-repeats 100 \
  --prepared-query-repeats 100 \
  --output docs/reports/goal1393_v1_5_stable_primitive_pod_results/stable_primitive_evidence.json
```

Result summary:

```text
scalar_statuses:
  COUNT_HITS: ok
  REDUCE_FLOAT(MAX): ok
  REDUCE_FLOAT(MIN): ok
  REDUCE_FLOAT(SUM): ok
  REDUCE_INT(COUNT): ok
  REDUCE_INT(SUM): ok

direct_anyhit_count:
  cpu: ok, hit_count 256
  embree: ok, hit_count 256
  optix: ok, hit_count 256

parity:
  embree: ok, hit_count_matches true, row_count_matches true
  optix: ok, hit_count_matches true, row_count_matches true
  optix_prepared_count: ok, hit_count_matches true

prepared_optix_anyhit_count:
  status: ok
  hit_count: 256

public_wording_authorized: false
```

Preserved artifacts:

- `docs/reports/goal1393_v1_5_stable_primitive_pod_results/rtdl_pod_env.json`
- `docs/reports/goal1393_v1_5_stable_primitive_pod_results/stable_primitive_evidence.json`

## Decision Impact

Goal1393 supplies fresh-Git pod evidence for the stable v1.5 primitive packet. It is still evidence input only: public wording and release/tag action remain blocked until the public wording packet and 3-AI consensus are recorded.
