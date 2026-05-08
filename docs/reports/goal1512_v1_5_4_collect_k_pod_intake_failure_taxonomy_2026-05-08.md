# Goal 1512: Collect-K Pod Intake Failure Taxonomy

## Verdict

No pod was available for new measurement. This note prepares the next pod
window by defining failure classes, acceptance criteria, and immediate commands
for OptiX `COLLECT_K_BOUNDED` stage profiling.

This is a runbook and taxonomy only. It does not authorize public speedup
wording, broad RTX wording, whole-app claims, true zero-copy wording, stable
primitive promotion, experimental public promotion, partner tensor handoff, or
release action.

## Immediate Pod Commands

Use a clean Git state on the pod:

```bash
git clone https://github.com/rubaolee/rtdl.git rtdl_pod_check
cd rtdl_pod_check
git rev-parse HEAD
```

Probe the environment before assuming a layout:

```bash
uname -a
command -v nvidia-smi && nvidia-smi || true
command -v nvcc && nvcc --version || true
python3 --version
```

If OptiX headers are missing, use a driver-compatible SDK tag rather than the
newest tag by default:

```bash
mkdir -p /root/vendor
git clone https://github.com/NVIDIA/optix-sdk /root/vendor/optix-sdk
cd /root/vendor/optix-sdk
git checkout v8.0.0
ln -sfn /root/vendor/optix-sdk /opt/optix
cd /root/rtdl_pod_check
```

Run the current evidence path:

```bash
OPTIX_PREFIX=/root/vendor/optix-sdk bash scripts/goal1506_v1_5_4_run_optix_collect_k_stage_profile_pod.sh
```

## Failure Taxonomy

| Class | Symptom | Classification | Next action |
| --- | --- | --- | --- |
| Environment missing NVIDIA driver | `nvidia-smi` missing or no GPU visible | Pod unusable for OptiX evidence | Stop GPU evidence run; record provider/GPU issue |
| CUDA missing but driver present | `nvidia-smi` works, `nvcc` missing | Build environment incomplete | Install CUDA toolkit or switch image; do not call this RTDL failure |
| OptiX headers missing | `make build-optix` cannot find headers | SDK setup issue | Clone/link compatible OptiX SDK and rerun |
| Driver/SDK mismatch | OptiX build or runtime rejects SDK/driver combination | Environment compatibility issue | Use compatible SDK tag such as OptiX 8.0 for 550.x drivers |
| Shared memory insufficient | Goal1508 says requested counts are not profile candidates | Hardware not accepted for tiled evidence | Treat as fallback smoke only; do not commit as performance evidence |
| Native path fallback | Profile native path differs from expected tiled path | Not accepted Goal1506 evidence | Use only for debugging; find capable GPU or fix dispatch |
| Topology mismatch | Tile/merge/copy/metadata counts differ from expected topology | Implementation or instrumentation drift | Stop and inspect native code before optimization |
| Parity failure | Candidate rows, valid count, or overflow flag mismatch | Correctness blocker | Fix correctness before performance work |
| Missing profile records | JSONL record count differs from expected warmup plus repeats | Instrumentation blocker | Fix profiling hook or runner before interpreting timings |
| High total time with clean gates | Accepted evidence but slow stage medians | Performance investigation target | Rank stage medians; optimize measured bottleneck only |

## Accepted Evidence Checklist

Accepted Goal1506 evidence requires all of the following:

- Real NVIDIA GPU visible to CUDA.
- `librtdl_optix.so` built from the recorded Git commit.
- Goal1508 preflight says all requested counts are profile candidates.
- Counts include `4097`, `65537`, and `131072`.
- Repeats are at least `5` after warmup.
- Parity passes for candidate rows, valid counts, and overflow flags.
- Profile JSONL contains expected records for warmup plus repeats.
- Native profile path matches `row_width2_bounded_multi_tile_sort_merge` for
  the target counts.
- Topology matches expected tile count, merge levels, sort launches, merge
  launches, carry copies, final copies, and metadata fields.
- JSON, Markdown, and JSONL artifacts are saved under `docs/reports/`.
- Claim flags remain false.

## Interpretation Rules

- Do not optimize from end-to-end timing alone if stage timings are available.
- Do not treat fallback smoke as accepted evidence.
- Do not compare pod timing against local GTX 1070 fallback timing as if they
  are the same path.
- Do not attribute slowness to OptiX, Python, or the DSL until the stage profile
  identifies the dominant bucket.
- Do not use true zero-copy language for this work. The current path is an
  experimental device-pointer bridge with explicit profiling, not a public
  partner-memory contract.

## Claim Boundary

Goal1512 is a pod intake and failure-classification runbook. It does not add new measurements.
It does not authorize public speedup wording, broad RTX wording, whole-app
claims, true zero-copy wording, stable primitive promotion, experimental public
promotion, partner tensor handoff, or release action.
