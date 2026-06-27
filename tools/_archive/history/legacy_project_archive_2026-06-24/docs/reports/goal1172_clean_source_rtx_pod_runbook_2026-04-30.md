# Goal1172 Clean-Source RTX Pod Runbook

Date: 2026-04-30

This runbook prepares a future clean-source pod session. It does not run cloud, does not authorize public wording, and must not be used with a copied dirty tree.

## Steps

### 1. clone_clean_source

Start from a clean pushed commit, not a copied dirty local tree.

```bash
git clone https://github.com/rubaolee/rtdl.git rtdl_clean
cd rtdl_clean
git checkout <pushed_commit_for_goal1170>
git status --short
```

### 2. install_linux_prerequisites

Install strict-reference and native-build dependencies before running gates.

```bash
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y build-essential git cmake pkg-config libgeos-dev python3-dev python3-pip cuda-nvrtc-dev-13-0 cuda-cudart-dev-13-0
```

### 3. prepare_optix_headers

Point the build at OptiX headers compatible with the pod driver/CUDA setup.

```bash
mkdir -p /root/vendor
git clone --depth 1 --branch v8.0.0 https://github.com/NVIDIA/optix-dev.git /root/vendor/optix-dev
export OPTIX_PREFIX=/root/vendor/optix-dev
export CUDA_PREFIX=/usr/local/cuda
export NVCC=/usr/local/cuda/bin/nvcc
export RTDL_OPTIX_PTX_COMPILER=nvcc
```

### 4. build_native_optix

Build the native OptiX backend once before preflight and app rows.

```bash
make build-optix OPTIX_PREFIX=$OPTIX_PREFIX CUDA_PREFIX=$CUDA_PREFIX NVCC=$NVCC 2>&1 | tee docs/reports/goal1170_clean_source_rtx_claim_grade_batch/make_build_optix.log
```

### 5. preflight

Fail fast before any benchmark if source or environment is not claim-grade ready.

```bash
PYTHONPATH=src:. python3 scripts/goal1171_clean_source_rtx_pod_preflight.py --output-json docs/reports/goal1170_clean_source_rtx_claim_grade_batch/goal1171_preflight.json --output-md docs/reports/goal1170_clean_source_rtx_claim_grade_batch/goal1171_preflight.md
```

### 6. run_goal1170_batch

Run all eight RTX rows in one pod session.

```bash
PYTHONPATH=src:. bash scripts/goal1170_clean_source_rtx_batch_runner.sh 2>&1 | tee docs/reports/goal1170_clean_source_rtx_claim_grade_batch/goal1170_runner.log
```

### 7. package_copyback

Copy back all logs and JSON artifacts before stopping the pod.

```bash
tar -czf /tmp/goal1170_clean_source_rtx_claim_grade_batch.tgz docs/reports/goal1170_clean_source_rtx_claim_grade_batch
sha256sum /tmp/goal1170_clean_source_rtx_claim_grade_batch.tgz > /tmp/goal1170_clean_source_rtx_claim_grade_batch.tgz.sha256
```

## Boundary

This runbook prepares a future clean-source pod session. It does not run cloud, does not authorize public wording, and must not be used with a copied dirty tree.
