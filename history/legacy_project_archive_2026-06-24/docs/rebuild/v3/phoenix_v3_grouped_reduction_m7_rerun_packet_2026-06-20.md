# Phoenix V3 Grouped-Reduction M7 Rerun Packet

Status: ready for external review, not executed.

```text
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
m7_promotion_authorized_before_run: false
```

## Purpose

This packet defines the fresh M7-designated grouped_reduction rerun. It does not promote grouped_reduction.
The rerun exists because the feasibility packet found useful evidence but also warmup asymmetry, setup/cold cost, and repeat-policy blockers.

## Prepared-Query Public Contract Draft

- A prepared-query row must show cold/setup time, hot prepared-query time, and repeat-aware totals together.
- Any speedup claim must name the repeat count or say hot prepared-query only.
- Single-query end-to-end speedup must be shown even when the intended workload is repeated.
- Whole-database or paper-reproduction wording remains false unless a separate packet authorizes it.
- Warmup count, repeats, backend, groups, rows, and hardware must be identical or explicitly explained.

## Planned Rows

| Row | Generated rows | Groups | Warmup | Output |
| --- | ---: | ---: | ---: | --- |
| `m7_grouped_reduction_262144` | 262144 | 1024 | 3 | `/root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_grouped_reduction_m7_20260620/m7_grouped_reduction_262144_warmup3.json` |
| `m7_grouped_reduction_524288` | 524288 | 2048 | 3 | `/root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_grouped_reduction_m7_20260620/m7_grouped_reduction_524288_warmup3.json` |

## Required Commands

### `env_probe`

Record GPU, source identity, Python environment, and artifact directory.

```bash
mkdir -p /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_grouped_reduction_m7_20260620 && nvidia-smi > /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_grouped_reduction_m7_20260620/nvidia-smi.txt && cat VERSION > /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_grouped_reduction_m7_20260620/source_version.txt && sha256sum VERSION scripts/v3_0_m28_raydb_prepared_grouped_refresh.py scripts/v3_optix_hardware_gate.py scripts/v3_gpu_python_env_gate.py scripts/v3_phoenix_grouped_reduction_m7_feasibility.py scripts/v3_phoenix_grouped_reduction_m7_rerun_packet.py > /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_grouped_reduction_m7_20260620/source_manifest.sha256 && PYTHONPATH=src:. /root/rtdl_v3_rebuild_20260620/.venv/bin/python scripts/v3_gpu_python_env_gate.py --json-out /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_grouped_reduction_m7_20260620/gpu_env_gate.json
```

### `claim_boundary_gate`

Fail if this packet drifts into release or public-claim authorization before measurement.

```bash
/root/rtdl_v3_rebuild_20260620/.venv/bin/python -c "import json,pathlib; p=pathlib.Path('docs/rebuild/v3/phoenix_v3_grouped_reduction_m7_rerun_packet_2026-06-20.json'); d=json.loads(p.read_text()); assert d['release_authorized'] is False; assert d['public_speedup_claim_authorized'] is False; assert d['whole_app_speedup_claim_authorized'] is False; assert d['m7_promotion_authorized_before_run'] is False; print('grouped reduction M7 rerun claim-boundary gate ok')" > /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_grouped_reduction_m7_20260620/claim_boundary_gate.txt 2>&1
```

### `optix_hardware_gate`

Require NVIDIA OptiX-capable hardware before measuring OptiX rows.

```bash
PYTHONPATH=src:. /root/rtdl_v3_rebuild_20260620/.venv/bin/python scripts/v3_optix_hardware_gate.py --require-rt-hardware --json-out /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_grouped_reduction_m7_20260620/optix_hardware_gate.json
```

### `native_build`

Build native Embree and OptiX libraries for the measured tree.

```bash
make build-embree build-optix OPTIX_PREFIX=/workspace/vendor/optix-dev-8.0.0
```

### `m7_grouped_reduction_262144`

Run fresh grouped_reduction rows at 262144 generated rows with standardized warmup=3.

```bash
PYTHONPATH=src:. /root/rtdl_v3_rebuild_20260620/.venv/bin/python scripts/v3_0_m28_raydb_prepared_grouped_refresh.py --generated-rows 262144 --generated-groups 1024 --modes count,sum --backends embree,optix --warmup 3 --include-iteration-walls --output /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_grouped_reduction_m7_20260620/m7_grouped_reduction_262144_warmup3.json
```

### `m7_grouped_reduction_524288`

Run fresh grouped_reduction rows at 524288 generated rows with standardized warmup=3.

```bash
PYTHONPATH=src:. /root/rtdl_v3_rebuild_20260620/.venv/bin/python scripts/v3_0_m28_raydb_prepared_grouped_refresh.py --generated-rows 524288 --generated-groups 2048 --modes count,sum --backends embree,optix --warmup 3 --include-iteration-walls --output /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_grouped_reduction_m7_20260620/m7_grouped_reduction_524288_warmup3.json
```

### `post_run_intake`

Compute repeat-aware totals from the fresh warmup=3 rows.

```bash
PYTHONPATH=src:. /root/rtdl_v3_rebuild_20260620/.venv/bin/python scripts/v3_phoenix_grouped_reduction_m7_feasibility.py --fresh-rerun --source m7_262144=/root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_grouped_reduction_m7_20260620/m7_grouped_reduction_262144_warmup3.json --source m7_524288=/root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_grouped_reduction_m7_20260620/m7_grouped_reduction_524288_warmup3.json --json-out /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_grouped_reduction_m7_20260620/m7_grouped_reduction_post_run_intake.json --md-out /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_grouped_reduction_m7_20260620/m7_grouped_reduction_post_run_intake.md
```

### `artifact_manifest`

Record final artifact file list after measurement.

```bash
find /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_grouped_reduction_m7_20260620 -maxdepth 2 -type f | sort > /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_grouped_reduction_m7_20260620/artifact_file_index.txt
```

## Acceptance Checks

- The packet claim-boundary gate passes on the pod before measurement.
- OptiX hardware gate passes before measurement.
- Native Embree and OptiX libraries build in the measured source tree.
- Both planned scales run with warmup=3 and include independent Embree/OptiX count/sum rows.
- Every row records cold_prepare_total_sec, workload_build_sec, elapsed_median_sec, repeat, and warmup.
- Every row matches CPU reference and keeps public/release claim flags false.
- Post-run intake computes repeat-aware totals for repeat counts 1, 2, 5, 10, 25, 50, 100, 500, and 1000.
- No public wording is written until an external review accepts the rerun and a Codex consensus records the exact allowed claim.

## Goal-Level Decision Audit

Decision: prepare a fresh M7-designated grouped_reduction rerun packet before using pod time

1. Was I foolish?

   No. The feasibility packet showed that old warmup-asymmetric evidence is not enough for promotion.

2. If yes, what actions made the decision foolish?

   It would be foolish to rerun ad hoc or reuse old warmup=1/2 rows as a release row.

3. Was there another path?

   Run the pod immediately. That would risk another unreviewed evidence surface.

4. Can I now try a different path that actually solves the problem?

   Freeze the rerun contract locally, test it, then seek review before execution.
