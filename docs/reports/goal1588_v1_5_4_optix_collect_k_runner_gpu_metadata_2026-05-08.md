# Goal 1588: OptiX Collect-K Runner GPU Metadata

## Verdict

The Goal1586 multi-session runner now records usable GPU metadata for future architecture-specific validation packages. This closes a practical evidence-management gap for the next non-Ada pod run.

## What Changed

The runner records:

- optional human device label from `--device-label`,
- `nvidia-smi --query-gpu=name,driver_version`,
- CUDA version parsed from the `nvidia-smi` banner,
- per-device `name`, `driver_version`, and `cuda_version` in the JSON summary.

The metadata query avoids unsupported `nvidia-smi` fields such as `cuda_version` and `compute_cap`, which caused the first metadata smoke to report `unavailable`.

## Validation

Local:

- `$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal1586_v1_5_4_optix_collect_k_multi_session_runner_test`
- Result: `Ran 3 tests`, `OK`.

Pod:

- Commit: `4af9c1ed`
- Command shape: `scripts/goal1586_v1_5_4_optix_collect_k_multi_session_validation_runner.py --sessions 1 --device-label ada_metadata_smoke`
- Result: `goal1586_multi_session_validation_recorded`.
- Metadata JSON:

```json
{
  "device_label": "ada_metadata_smoke",
  "devices": [
    {
      "cuda_version": "12.8",
      "driver_version": "550.127.05",
      "name": "NVIDIA RTX 4000 Ada Generation"
    }
  ],
  "nvidia_smi_cuda_version": "12.8",
  "nvidia_smi_query": "NVIDIA RTX 4000 Ada Generation, 550.127.05"
}
```

## Claim Boundary

This report documents evidence tooling only. It does not authorize public speedup wording, true zero-copy wording, stable primitive promotion, whole-application claims, or release action.
