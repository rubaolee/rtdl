# Pod Validation Next Steps

Current date: 2026-05-12

## Current State

Local and LAN validation are complete up to the non-release-hardware boundary:

- Windows Oracle toolchain fix is documented in Goal1710.
- Linux source, Embree/oracle, OptiX build, and OptiX smoke validation are
  documented in Goal1711.
- Gemini reviewed Goal1711 in Goal1712 with `accept-with-boundary`.
- Release readiness remains `needs-more-evidence` because accepted pod/hardware
  validation is still absent.

## Pod Requirement

Use a suitable NVIDIA pod for release evidence. The LAN GTX 1070 at
`192.168.1.20` is useful smoke hardware, but project memory says it is not
accepted release hardware evidence for the relevant v1.6.11/v1.8 NVIDIA path.

## First Pod Commands

After the user provides the pod SSH command, record the exact command in the
Goal1714 report and run:

```bash
hostname
uname -a
nvidia-smi
which python3 || true
python3 --version || true
which nvcc || true
nvcc --version || true
```

Probe OptiX SDK:

```bash
find /opt /usr/local /root /workspace -maxdepth 4 -type f -name optix.h 2>/dev/null | head -20
```

If headers are missing and network is available, use the project-memory path:

```bash
mkdir -p /root/vendor
cd /root/vendor
git clone https://github.com/NVIDIA/optix-sdk optix-sdk
cd optix-sdk
git checkout v8.0.0
ln -sfn /root/vendor/optix-sdk /opt/optix
```

## Source Setup

Prefer a fresh clone from Git if the current commits are pushed:

```bash
git clone https://github.com/rubaolee/rtdl /workspace/rtdl_goal1714
cd /workspace/rtdl_goal1714
git checkout main
git rev-parse HEAD
```

If current local changes are not pushed, sync an archive from Windows or the
LAN staging directory, explicitly excluding:

```text
docs/reports/goal1204_rtdl_source_2026-05-01.tar.gz
```

## Validation Slice

Build native libraries:

```bash
make build-optix OPTIX_PREFIX=/opt/optix
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1711_optix_source_recovery_and_linux_build_validation_test \
  tests.goal1708_source_recovery_and_semantic_cleanup_test \
  tests.goal1699_db_to_columnar_payload_native_migration_test \
  tests.goal1673_optix_pose_to_group_native_migration_test \
  tests.goal1668_native_engine_app_agnostic_directive_test -q
```

Runtime smoke:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal903_embree_graph_ray_traversal_test \
  tests.goal671_optix_prepared_anyhit_count_test \
  tests.goal933_prepared_segment_polygon_optix_test -q
```

If the pod is suitable for performance evidence, run the current v1.6.11/v1.8
pod matrix specified by the latest Goal1659/Goal1660/Goal1711 reports before
making release claims.

## Required Output

Write:

```text
docs/reports/goal1714_pod_hardware_validation_after_source_recovery_2026-05-12.md
```

The report must include:

- exact pod SSH command,
- GPU name and driver,
- source setup method and commit/archive source,
- OptiX SDK path,
- commands run,
- pass/fail output summaries,
- whether evidence is smoke-only or release-acceptable,
- explicit `needs-more-evidence` boundary unless release-acceptable hardware
  evidence is actually produced and independently reviewed.

