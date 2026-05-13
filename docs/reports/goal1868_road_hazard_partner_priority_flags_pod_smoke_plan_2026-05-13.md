# Goal1868 - Road Hazard Partner Priority Flags Pod Smoke

Status: pass-with-boundary

Date: 2026-05-13

## Scope

Goal1868 adds and validates a progress-printing pod-smoke runner for the Goal1865
`road_hazard_screening` partner priority-flag adapter:

`scripts/goal1868_road_hazard_partner_priority_flags_pod_smoke.py`

The runner builds caller-owned Torch/CuPy CUDA columns, invokes:

`rtdsl.road_hazard_priority_flags_optix_partner_device_columns(...)`

and validates partner-owned:

- `road_ids`
- `hit_counts`
- `priority_flags`

against deterministic expected counts and threshold flags.

## Pod Command

```bash
PYTHONPATH=src:. python3 scripts/goal1868_road_hazard_partner_priority_flags_pod_smoke.py \
  --count 16 \
  --threshold 2 \
  --partners cupy,torch \
  --output docs/reports/goal1868_road_hazard_partner_priority_flags_pod_smoke.json
```

The runner prints `[setup]`, `[partner]`, and `[artifact]` progress markers so a
long pod run is not silent.

## Pod Evidence

Artifact:

`docs/reports/goal1868_road_hazard_partner_priority_flags_pod_smoke.json`

Pod:

- SSH: `root@213.192.2.116 -p 40189`
- Key used by Codex: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`
- GPU: `NVIDIA GeForce RTX 3090, 580.126.20`
- Commit: `0a96e139a7d584e56e6dd05539ad66e3370aa9d7`

Both CuPy and Torch produced the expected deterministic columns:

- `hit_counts`: alternating `2, 1, ...`
- `priority_flags`: alternating `1, 0, ...`
- `native_engine_row_contract: generic_ray_primitive_witness_pairs`
- `v2_0_release_authorized: false`
- `whole_app_speedup_claim_authorized: false`

The pod run also caught and fixed a Torch CUDA boundary issue: CUDA `uint32`
comparison is unsupported by `torch.ge`, so Goal1865 now casts hit counts to
`int64` before threshold comparison and returns `uint32` flags.

## Boundary

This is a pod smoke for one app adapter. It does not authorize v2.0 release
wording, whole-application speedup wording, broad RT-core speedup wording, or an
all-app v2.0-vs-v1.8 performance table.
