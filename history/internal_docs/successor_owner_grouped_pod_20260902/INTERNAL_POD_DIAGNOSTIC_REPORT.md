# Internal Pod diagnostic: successor owner-grouped any-hit

Date: 2026-09-02

Review class: internal execution diagnostic, not external review

Verdict:
`OPTIX8_BOUNDED_DIAGNOSTIC_PASS__OPTIX9_FORMAL_GATE_BLOCKED_BY_DRIVER_ABI`

## Claim boundary

This report records one clean-checkout GPU diagnostic of the app-neutral
`OWNER_GROUPED_ANY_HIT / BOOL_OR` route and its bounded linear RT-CCD case
study. It authorizes no speedup, benchmark-app, Paper App, full-paper,
same-input-author-code, OptiX 9 formal-gate, or external-consensus claim.

The OptiX 8 execution is deliberately diagnostic because the registered target
is OptiX 9. Timings were collected by the runner for troubleshooting only:
`registered_performance_timing_count=0` and `performance_claimed=false`.

## Source and host identity

- SSH endpoint: `root@213.173.108.10`, port `15540`.
- SSH key path: `/Users/rl2025/.ssh/id_ed25519_rtdl_codex`.
- Pod checkout: `/workspace/rtdl`, clean branch
  `codex/cgo-goal5836-handoff`.
- Executed commit: `2c48337bda79a8bda3f3d123df6be393f88c4e95`.
- GPU: NVIDIA RTX 4000 Ada Generation,
  `GPU-b0ed3da9-0c28-b259-37a1-d1a36d836ab7`, compute capability 8.9.
- Driver: 550.127.05.
- Platform: Linux 6.8.0-40 x86_64, glibc 2.39; Python 3.12.3.
- CUDA: 12.8, `nvcc` 12.8.93; host compiler GCC 13.3.0.
- Python stack: NumPy 2.4.4, Numba 0.65.1, llvmlite 0.47.0.
- Geometry dependency: GEOS 3.12.1.
- OptiX 9 headers: NVIDIA `optix-dev` tag `v9.0.0`, commit
  `083bffe2011019ca2b9078f53206ff9f0193b63a`.
- OptiX 8 diagnostic headers: NVIDIA `optix-dev` tag `v8.0.0`, commit
  `bef93afb12dbd00e5b8311bc9b320dd487d8cc1f`.

## OptiX 9 formal-target attempt

The then-current preflight v1 compiled the exact NVCC host probe, four Numba
callback leaves, and trusted NVRTC wrapper. It incorrectly reported readiness
for a GPU run because v1 tested compilation only. A fresh native library then
built and exported all four required owner-grouped C ABI symbols:

- native bytes: 7,192,472;
- native SHA-256:
  `650b1b3ccd4a92f67fac86e1f2d51b2976e0fd3529dd64e5884e5a85dcdfbccb`;
- build ID:
  `b6f44e07fad22a58a3197bef0e61e2987b54be17a0ed3f3da35f8d7b95636b74`.

The first workload failed during native prepare with
`OptiX error: Unsupported ABI version`. No OptiX launch occurred and no GPU
result was published. `RUN_INCOMPLETE.json` remained in the artifact directory
with status `INCOMPLETE__NO_GPU_RESULT_AUTHORIZED`. This is an environment
incompatibility, not successful OptiX 9 evidence.

## OptiX 8 bounded diagnostic

Changing only to the official OptiX 8 header snapshot allowed the same source
route to build and execute on the same host. The native library again exported
all four required symbols:

- native bytes: 7,192,472;
- native SHA-256:
  `2b840b57e6e259c0a16d764fd99a00917e651625464e93c8b31edcf602f523d8`;
- build ID:
  `221ceb83693e8978242b7b40139343dec8c242209711aeb05f7a4dd17b4d5e2f`.

The complete runner result was
`PASS__TRUE_OPTIX_PARITY_AND_PREPARED_REUSE`:

- six semantic workloads plus three deterministic scale workloads, 9/9;
- repeat count two, 18/18 true OptiX launches;
- 18/18 GPU executions matched the independent CPU oracle;
- all true-OptiX receipts and prepared-reuse counts validated;
- zero registered performance timings;
- zero external reviews;
- no author-code, Paper App, full reproduction, or benchmark-app claim.

## Remediation triggered by the failure

Preflight has been upgraded locally to schema
`rtdl.successor_owner_grouped_any_hit.pod_preflight.v2`. Before compiling the
callback stack it now builds and runs a temporary `optixInit()` probe against
the selected headers and host driver. The probe performs zero `optixLaunch`
calls, records its source/binary/output identity on success, and rejects an ABI
mismatch before native-library construction. This remediation requires Pod
confirmation at the post-fix commit before it is treated as complete.

## Preserved artifacts

The complete compressed bundle is
`owner_grouped_pod_bundle_2c48337.tar.gz`, SHA-256
`6182a7f52116a0137baaf9d97900860aa61196d4bc783418a1779f9d93ab2d05`.

| Artifact | SHA-256 |
|---|---|
| OptiX 9 preflight v1 JSON | `b93344707ba245b382d55e15f1b7b51a20d982aaebbe0dfc8fe1e934291d5dd0` |
| OptiX 9 native manifest | `567c36e61f0ec0cc0352bbee3abb460ac6fef4594e0a05b9d7e6842cf23c0a0e` |
| OptiX 8 preflight v1 JSON | `0ebaf2509cdba3d1fa4aeac96b65de43c585188e5eeab717f8bd5128de39c56d` |
| OptiX 8 native manifest | `97b52dee4757a7938a16bc8a0ed552deb3c5931dc3fc33afe273a552cdb5f496` |
| OptiX 8 complete GPU result | `64c3d09bc661ef910be6d657d87a20854d4967b7f2cd514b16896fa0e93de639` |

Both native build logs are empty files with the SHA-256 of empty bytes because
the successful builder emitted no compiler diagnostics.

## Next exact gate

1. Commit the preflight-v2 remediation and validate that OptiX 9 fails during
   `optixInit()` on this driver before native build.
2. Validate that OptiX 8 passes the same zero-launch runtime ABI probe.
3. Obtain a Pod whose driver negotiates the pinned OptiX 9 ABI.
4. From a clean exact commit, rerun preflight v2, native build, and all nine
   workloads twice.
5. Preserve artifacts and perform the deferred external review before any
   promotion wording.
