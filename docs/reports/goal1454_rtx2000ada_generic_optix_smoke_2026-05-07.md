# Goal1454 RTX 2000 Ada Generic OptiX Smoke

## Verdict

Accepted as a latest-main generic OptiX compatibility/parity smoke on the RTX
2000 Ada pod. This is not a performance claim, not true zero-copy evidence, not
public speedup wording, not stable primitive promotion, and not a release
action.

## Run Scope

- Pod SSH target: `root@157.157.221.29 -p 57142`
- Key source used: `Z:\rtdl-dev\id_ed25519_rtdl_codex`
- Git HEAD: `0a92e3450c238e605b5097bd8ab0803f3466cd4c`
- GPU: NVIDIA RTX 2000 Ada Generation, 16 GB
- Runner: `scripts/goal1292_v1_5_generic_optix_evidence_runner.py`
- Fixture: `1000` copies, `2000` rays, `1000` triangles
- Corrected payload:
  `docs/reports/goal1454_rtx2000ada_generic_optix_smoke_2026-05-07/goal1454_generic_optix_payload_rerun.json`

## Outcome

- CPU direct status: `ok`
- Embree direct status: `ok`
- OptiX direct status: `ok`
- Prepared OptiX status: `ok`
- Embree parity: hit count and rows match CPU
- OptiX parity: hit count and rows match CPU
- Prepared OptiX count parity: hit count matches CPU

## Note

The first payload in the artifact directory used a malformed Windows-origin
`RTDL_OPTIX_LIB` path and is diagnostic only. The accepted rerun explicitly set
`RTDL_OPTIX_LIB=/root/rtdl_goal1454_rtx_smoke/build/librtdl_optix.so`.

## Boundary

This smoke confirms generic raw ray/triangle `ANY_HIT` plus `COUNT_HITS`
compatibility on the RTX pod. It does not measure speed, does not prove true
zero-copy, does not authorize whole-app claims, does not promote any primitive
to stable, and does not publish or release anything.
