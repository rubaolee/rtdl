# Internal Pod validation: successor owner-grouped any-hit

Date: 2026-09-02

Review class: internal execution diagnostic, not external review

Verdict:
`OPTIX8_INTERNAL_GPU_FUNCTIONAL_GATE_PASS__OPTIX9_COVERAGE_UNAVAILABLE_ON_R550`

## Claim boundary

This report records clean-checkout GPU functional validation of the app-neutral
`OWNER_GROUPED_ANY_HIT / BOOL_OR` route and its bounded linear RT-CCD case
study. It authorizes no speedup, benchmark-app, Paper App, full-paper,
same-input-author-code, broad OptiX-version, or external-consensus claim.

OptiX 8.0 is the exact internal functional profile because this route uses no
OptiX 9-specific API and NVIDIA supports OptiX 8.0 on R535 or newer. The exact
decision is in
`../successor_owner_grouped_optix_profile_decision_20260902.md`. Timings were
collected by the runner for troubleshooting only:
`registered_performance_timing_count=0` and `performance_claimed=false`.

## Source and host identity

- SSH endpoint: `root@213.173.108.10`, port `15540`.
- SSH key path: `/Users/rl2025/.ssh/id_ed25519_rtdl_codex`.
- Pod checkout: `/workspace/rtdl`, clean branch
  `codex/cgo-goal5836-handoff`.
- Initial executed commit:
  `2c48337bda79a8bda3f3d123df6be393f88c4e95`.
- Post-fix executed commit:
  `5ee0e9404a1262decca6176642edc9f764d8c3f3`.
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

## OptiX 9 compatibility attempt

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

## OptiX 8 internal functional validation

Changing only to the official OptiX 8 header snapshot allowed the same source
route to build and execute on the same host. No frozen successor authority or
implementation feature required OptiX 9. The native library again exported all
four required symbols:

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

Preflight was upgraded to schema
`rtdl.successor_owner_grouped_any_hit.pod_preflight.v2`. Before compiling the
callback stack it now builds and runs a temporary `optixInit()` probe against
the selected headers and host driver. The probe performs zero `optixLaunch`
calls, records its source/binary/output identity on success, and rejects an ABI
mismatch before native-library construction.

The same Pod confirmed both branches at post-fix commit `5ee0e94`:

- OptiX 9 failed with exit code 1 and `optixInit_result=7801`; no PASS JSON,
  callback-stack compilation, native build, or OptiX launch followed.
- OptiX 8 produced schema v2 status
  `PASS__COMPILER_AND_OPTIX_RUNTIME_ABI_READY_FOR_NATIVE_BUILD`, with
  `optixInit_result=0`, all four callback roles compiled, and zero launches.
- A fresh post-fix OptiX 8 native build produced SHA-256
  `bc093c2db1987997565d006f3b1061d8cfbfca4a4f6e4886edb5b2e0279458ed`
  and build ID
  `477f50bbdb49b2d4cc4832f62c3de56916fbaa271ffc39a2be4353725e0244b6`.
- The fresh app-front-door run repeated 9/9 workloads, 18/18 true-OptiX
  launches, 18/18 oracle matches, valid traversal receipts, and prepared reuse.
- Pod regressions passed 50/50 successor tests and 168/168 frozen
  Goal5833--Goal5836 tests.

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
| Post-fix OptiX 9 ABI-failure log | `ca3c84bccce74f31db9ed7d66099b6d87b78275e4554275226059201a6ef2527` |
| Post-fix OptiX 9 exit-code file | `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865` |
| Post-fix OptiX 8 preflight v2 JSON | `900271b8e2b897a4c5e71248f424119e15dc0c9539b35d30d26da4c72fad7cd8` |
| Post-fix OptiX 8 native manifest | `973ecf423fb1e58a95aaa56134fdf607c868c522a5d14a07305867647bcb99bd` |
| Post-fix OptiX 8 complete GPU result | `9fac2dc7b70565a0dbb7c455b16aac73e94beba06cb180e0bd6dd45857805551` |

The post-fix bundle is `owner_grouped_postfix_bundle_5ee0e94.tar.gz`,
SHA-256
`e04f373a4ffc203aad1914e7310c66253763634933479b69f03119152e6c653b`.

All native build logs are empty files with the SHA-256 of empty bytes because
the successful builder emitted no compiler diagnostics.

## Remaining separate gates

1. Preserve final runner-schema-v2 artifacts from the exact post-decision
   commit on this Pod.
2. Perform the owner-deferred external review before consensus or public
   promotion wording.
3. Preregister an Embree/timing protocol before benchmark or speedup claims.
4. Use R570-or-newer hardware only if separate OptiX 9 coverage is desired.
