#!/usr/bin/env bash
set -euo pipefail

DURABLE_ROOT=${DURABLE_ROOT:-/workspace/rtdl-particle-110dee7aa-durable}
SOURCE_ROOT=${SOURCE_ROOT:-/tmp/rtdl-particle-110dee7aa}
PYTHON=${PYTHON:-/tmp/rtdl-crossgpu/venv/bin/python}
OPTIX_INCLUDE=${OPTIX_INCLUDE:-/tmp/rtdl-crossgpu/optix-dev/include}
CUDA_INCLUDE=${CUDA_INCLUDE:-/usr/local/cuda-12.8/targets/x86_64-linux/include}

export CUDA_HOME=${CUDA_HOME:-/tmp/rtdl-crossgpu/venv/lib/python3.12/site-packages/nvidia/cuda_nvcc}
export NUMBA_CUDA_USE_NVIDIA_BINDING=1
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH:-/tmp/rtdl-crossgpu/venv/lib/python3.12/site-packages/nvidia/cuda_nvrtc/lib:/tmp/rtdl-crossgpu/venv/lib/python3.12/site-packages/optix:/usr/local/cuda-12.8/targets/x86_64-linux/lib}
export PYTHONPATH="$SOURCE_ROOT/src:$SOURCE_ROOT"

OUTPUT=${OUTPUT:-$DURABLE_ROOT/replay_from_durable_v2}
OBSERVED_OUTPUT=${OBSERVED_OUTPUT:-$DURABLE_ROOT/data/observed_output_u32_replay_v2.npy}

cd "$SOURCE_ROOT"
"$PYTHON" "$DURABLE_ROOT/successor_v2/postformal_particle_reconstruct_durable_v2.py" \
  --source-root "$SOURCE_ROOT" \
  --archive "$DURABLE_ROOT/artifacts/formal/rtdl-authored-particle-formal-110dee7aa.tar.gz" \
  --base-particle-dir "$DURABLE_ROOT/data/base_particle" \
  --ensemble-dir "$DURABLE_ROOT/data/transition_ensemble" \
  --native "$DURABLE_ROOT/artifacts/native/librtdl_optix.so" \
  --optix-include "$OPTIX_INCLUDE" \
  --cuda-include "$CUDA_INCLUDE" \
  --output "$OUTPUT" \
  --save-observed-output "$OBSERVED_OUTPUT"
