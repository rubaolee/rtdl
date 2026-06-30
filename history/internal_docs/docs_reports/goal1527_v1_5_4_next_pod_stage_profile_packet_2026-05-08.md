# Goal 1527: Next Pod Stage-Profile Packet

## Verdict

The next paid NVIDIA pod round should run the Goal1506 OptiX
`COLLECT_K_BOUNDED` stage-profile runner from current `main`, not a broad
discovery rerun.

Local Windows and Linux preparation is already green through Goal1526. The
remaining pod-only question is accepted tiled-path stage timing on a GPU whose
Goal1508 preflight accepts the row_width=2 target counts.

## Pod Command

From a fresh pod shell:

```bash
git clone https://github.com/rubaolee/rtdl.git /root/rtdl
cd /root/rtdl
git pull --ff-only
git rev-parse HEAD

if [ ! -d /root/vendor/optix-sdk ]; then
  mkdir -p /root/vendor
  git clone https://github.com/NVIDIA/optix-sdk /root/vendor/optix-sdk
fi
cd /root/vendor/optix-sdk
git checkout v8.0.0
cd /root/rtdl

OPTIX_PREFIX=/root/vendor/optix-sdk \
COUNTS="4097 65537 131072" \
REPEATS=5 \
bash scripts/goal1506_v1_5_4_run_optix_collect_k_stage_profile_pod.sh
```

If the pod driver requires a different OptiX SDK tag, record the driver version,
the selected SDK tag, and the reason in the intake report. Do not silently change
the SDK.

## Required Artifacts

The run should produce or preserve:

- `docs/reports/goal1508_v1_5_4_optix_collect_k_tiled_preflight_2026-05-08.json`
- `docs/reports/goal1508_v1_5_4_optix_collect_k_tiled_preflight_2026-05-08.md`
- `docs/reports/goal1506_v1_5_4_optix_collect_k_stage_profile_probe_2026-05-08.json`
- `docs/reports/goal1506_v1_5_4_optix_collect_k_stage_profile_probe_2026-05-08.md`
- `docs/reports/goal1506_v1_5_4_optix_collect_k_stage_profile_probe_2026-05-08.jsonl`
- the full terminal transcript, including `nvidia-smi`, `git rev-parse HEAD`,
  `make build-optix`, and unittest output.

## Accepted Evidence Conditions

Treat the pod round as accepted Goal1506 evidence only if:

- Goal1508 marks counts `4097`, `65537`, and `131072` as accepted tiled-profile
  candidates;
- Goal1506 reports `accepted_goal1506_evidence=true`;
- every case preserves parity and fail-closed behavior;
- every case has the expected `row_width2_bounded_multi_tile_sort_merge` native
  path;
- every case has expected topology for tile count, merge levels, sort launches,
  merge launches, carry copies, final copies, and metadata fields downloaded;
- the runner's unittest slice passes.

## Failure Handling

If any accepted-evidence condition fails, save the artifacts anyway and classify
the result precisely as one of:

- SDK/build failure;
- preflight rejected hardware;
- fallback path only;
- parity failure;
- profile-record missing;
- topology mismatch;
- unittest failure.

Do not infer performance conclusions from a failed packet.

## Claim Boundary

This packet is execution guidance only. It does not authorize public speedup
wording, broad RTX/GPU claims, true zero-copy wording, whole-app claims, stable
`COLLECT_K_BOUNDED` promotion, or release action.
