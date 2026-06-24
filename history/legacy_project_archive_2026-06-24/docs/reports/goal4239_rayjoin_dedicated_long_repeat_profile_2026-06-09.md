# Goal4239 RayJoin Dedicated Long-Repeat Profile

Date: 2026-06-09

Status: internal RayJoin long-repeat evidence accepted with boundary

## Purpose

Goal4239 closes the weakest measurement note called out in the Goal4232 review:
the current ten-app closure had a representative RayJoin wall-time row, but not
a dedicated RayJoin long-repeat profile suitable for a future public-table
rehearsal.

This goal reruns the RayJoin representative public-CDB profile with larger
repeat counts on RTX 4000 Ada. It does not change route policy and does not
collapse RayJoin into a single paper-reproduction number.

## Environment

| Field | Value |
| --- | --- |
| Source commit | `048d940c86ffa6f7dd39db6c7bb16666cd0c9e21` |
| Source short | `048d940c` |
| Pod status at payload capture | clean (`git_status_short == ""`) |
| GPU | `NVIDIA RTX 4000 Ada Generation, 550.127.08` |
| Data | bounded public-CDB county/soil slices |

## Run Shape

| Parameter | Value |
| --- | ---: |
| Main repeat | `200` |
| Main warmup | `20` |
| PIP batch single repeat | `50` |
| PIP batch repeat | `40` |
| PIP batch request counts | `1`, `100` |
| Wrapper elapsed sec | `20.758453957736492` |
| Counts matched | `true` |

## Contract Results

| Contract | Recommended route | Numba hot median sec | RTDL/OptiX hot median sec | Ratio / Reading |
| --- | --- | ---: | ---: | --- |
| PIP one-shot | Numba CUDA JIT scalar count | `0.0004306621849536896` | `0.0017560124397277832` | RTDL/OptiX `0.245x` vs Numba; keep Numba for this bounded one-shot slice |
| PIP repeated requests | RTDL/OptiX prepared batch executor | n/a | n/a | per-request speedup vs single request `1.234x`; throughput evidence, not one-shot latency |
| LSI scalar count | RTDL/OptiX prepared segment-pair count | `0.023331668227910995` | `0.00008878111839294434` | RTDL/OptiX `262.800x` vs Numba |
| Overlay active count | RTDL/OptiX prepared shape-pair active count | `0.039719101041555405` | `0.00018619373440742493` | RTDL/OptiX `213.321x` vs Numba |

## Reading

The RayJoin route split remains stable under a longer run:

- bounded PIP one-shot stays a Numba route,
- repeated PIP requests favor the prepared RTDL/OptiX batch executor,
- LSI scalar count strongly favors prepared RTDL/OptiX,
- overlay active count strongly favors prepared RTDL/OptiX,
- automatic dispatch remains disabled and route choice stays visible.

This is better evidence than the earlier Goal4230 representative row because
RayJoin itself now has a dedicated long-repeat profile above the 10-second level.

## Boundary

Goal4239 does not authorize release action, public speedup wording, whole-app
acceleration wording, broad RT-core wording, RayJoin paper-reproduction wording,
RTDL-beats-RayJoin wording, true-zero-copy wording, automatic partner selection,
AMD performance wording, or app-specific native-engine logic.
