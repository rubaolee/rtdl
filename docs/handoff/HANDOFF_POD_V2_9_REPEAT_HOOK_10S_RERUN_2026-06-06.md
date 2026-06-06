# Handoff - v2.9 Repeat-Hook 10s Pod Rerun

Use this after Goal3542 review intake. The purpose is to rerun the v2.8-vs-v2.3 10-second steady-state packet after the five formerly partial rows gained resident repeat hooks.

## Preconditions

- Goal3542 implementation is committed and pushed to `origin/main`.
- The v2.3 evidence checkout has the same measurement-only repeat controls, or a documented same-contract measurement adapter is used. Do not interpret current-tree dry planning as historical v2.3 evidence.
- A NVIDIA pod is available with enough time for long runs.
- OptiX SDK headers are installed or installable at `/root/vendor/optix-sdk`.
- `build/librtdl_optix.so` builds from source with a CUDA toolkit compatible with the pod driver.

## Setup Sketch

```bash
set -euxo pipefail

git clone https://github.com/rubaolee/rtdl.git /root/rtdl_v29_current
cd /root/rtdl_v29_current
git checkout main
git pull --ff-only origin main

nvidia-smi --query-gpu=name,driver_version --format=csv,noheader
mkdir -p /root/vendor
if [ ! -d /root/vendor/optix-sdk ]; then
  git clone --depth 1 --branch v8.0.0 https://github.com/NVIDIA/optix-sdk /root/vendor/optix-sdk
fi
ln -sfn /root/vendor/optix-sdk /opt/optix
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk

export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
```

If the pod has CUDA 13 as `/usr/local/cuda` and generated PTX fails with an unsupported-toolchain error, rebuild with a CUDA 12 toolkit as documented in `C:\Users\Lestat\Desktop\refresh.md`.

## Evidence Command

Use the previous Goal3536 final packet as the seed artifact, but run from the current tree after Goal3542:

```bash
mkdir -p docs/reports/goal3545_v2_9_repeat_hook_10s_rerun_a5000

python3 scripts/goal3536_v2_8_vs_v2_3_10s_steady_state.py \
  --v23-root /root/rtdl_v29_current \
  --v28-root /root/rtdl_v29_current \
  --seed-artifact docs/reports/goal3536_v2_8_vs_v2_3_10s_steady_state_a5000/summary_final.json \
  --artifact-dir docs/reports/goal3545_v2_9_repeat_hook_10s_rerun_a5000 \
  --output docs/reports/goal3545_v2_9_repeat_hook_10s_rerun_a5000/summary.json \
  --target-measured-sec 10 \
  --repeat-safety-factor 1.5 \
  --timeout-sec 1800 | tee docs/reports/goal3545_v2_9_repeat_hook_10s_rerun_a5000/run.log
```

The `--v23-root`/`--v28-root` placeholders above intentionally use the same current tree for smoke planning only. For the authoritative comparison, replace them with the same-contract v2.3 evidence checkout and v2.9/current checkout used by the Goal3536 protocol. If the historical v2.3 checkout lacks repeat controls, first apply a measurement-only adapter/backport and record it explicitly in the report.

## Acceptance Checks

- The fresh summary has all 11 comparison rows.
- The five Goal3542 rows are no longer partial because of missing repeat hooks.
- Each side of each final row reaches the 10-second measured hot-query target.
- Claim boundary flags remain false.
- The report explains any remaining weak rows by contract and phase, not by broad release wording.

## Non-Claims

This rerun does not automatically authorize release, public speedup claims, whole-app claims, broad RT-core claims, true zero-copy claims, or paper-reproduction claims. Those require a written report plus external review.
