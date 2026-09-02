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
- Controlling final executed commit:
  `7ec6b673b1da3dbe63ff2915e82d61f5302bf85c`.
- GPU: NVIDIA RTX 4000 Ada Generation,
  `GPU-b0ed3da9-0c28-b259-37a1-d1a36d836ab7`, compute capability 8.9.
- Driver: 550.127.05.
- Platform: Linux 6.8.0-40 x86_64, glibc 2.39; Python 3.12.3.
- CUDA: 12.8, `nvcc` 12.8.93; host compiler GCC 13.3.0.
- Python stack: NumPy 2.4.4, Numba 0.65.1, llvmlite 0.47.0.
- Geometry dependency: GEOS 3.12.1.
- OptiX 9 headers: NVIDIA `optix-dev` tag `v9.0.0`, commit
  `083bffe2011019ca2b9078f53206ff9f0193b63a`.
- OptiX 8 functional headers: NVIDIA `optix-dev` tag `v8.0.0`, commit
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
implementation feature required OptiX 9. At the controlling clean commit, the
native library exported all four required symbols:

- native bytes: 7,192,472;
- native SHA-256:
  `84a08dd78a60336cb94715d3ef9dcedb02828e60085d9906233645badb14e282`;
- build ID:
  `0d5095fe89c51d9828b767b0b174426c7c073e6b3014db8fac4149751c3ce2ee`.

The complete runner result was
`PASS__TRUE_OPTIX_PARITY_AND_PREPARED_REUSE`:

- six semantic workloads plus four deterministic scale workloads, 10/10;
- repeat count three, 30/30 true OptiX launches;
- 30/30 GPU executions matched the independent CPU oracle;
- all true-OptiX receipts and prepared-reuse counts validated;
- the largest workload used 512 owners, 4,096 primitives, and 1,024 queries;
  its independent oracle evaluated 4,194,304 pairs, found 1,024 intersecting
  pairs, and all three prepared GPU executions matched;
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

The same Pod confirmed both branches at controlling commit `7ec6b67`:

- OptiX 9 failed with exit code 1 and `optixInit_result=7801`; no PASS JSON,
  callback-stack compilation, native build, or OptiX launch followed.
- OptiX 8 produced schema v2 status
  `PASS__COMPILER_AND_OPTIX_RUNTIME_ABI_READY_FOR_NATIVE_BUILD`, with
  `optixInit_result=0`, all four callback roles compiled, and zero launches.
- A fresh OptiX 8 native build produced SHA-256
  `84a08dd78a60336cb94715d3ef9dcedb02828e60085d9906233645badb14e282`
  and build ID
  `0d5095fe89c51d9828b767b0b174426c7c073e6b3014db8fac4149751c3ce2ee`.
- The fresh app-front-door run repeated 10/10 workloads three times: 30/30
  true-OptiX launches, oracle matches, traversal receipts, and prepared-reuse
  checks passed.
- Pod regressions passed 51/51 successor tests and 168/168 frozen
  Goal5833--Goal5836 tests.

## Preserved artifacts

The initial diagnostic bundle is
`owner_grouped_pod_bundle_2c48337.tar.gz`, SHA-256
`6182a7f52116a0137baaf9d97900860aa61196d4bc783418a1779f9d93ab2d05`.

The controlling final bundle is
`owner_grouped_final_bundle_7ec6b67.tar.gz`, SHA-256
`8946473aea9bb4598e830d3a78771407c6798618cd3f4ab789fc280cf62d4b9d`.
Its standalone checksum manifest is
`owner_grouped_final_7ec6b67_SHA256SUMS`, SHA-256
`b1efde198887b8d8ecce2873d6702026833f230382e9dd3232931a39118ec837`.

| Artifact | SHA-256 |
|---|---|
| OptiX 9 preflight v1 JSON | `b93344707ba245b382d55e15f1b7b51a20d982aaebbe0dfc8fe1e934291d5dd0` |
| OptiX 9 native manifest | `567c36e61f0ec0cc0352bbee3abb460ac6fef4594e0a05b9d7e6842cf23c0a0e` |
| OptiX 8 preflight v1 JSON | `0ebaf2509cdba3d1fa4aeac96b65de43c585188e5eeab717f8bd5128de39c56d` |
| OptiX 8 native manifest | `97b52dee4757a7938a16bc8a0ed552deb3c5931dc3fc33afe273a552cdb5f496` |
| OptiX 8 complete GPU result | `64c3d09bc661ef910be6d657d87a20854d4967b7f2cd514b16896fa0e93de639` |
| Final OptiX 9 ABI-failure log | `a0887dc1de3f7ac7291463755821aa5d9eef5de8364a049f63d5fa3a60e43f4f` |
| Final OptiX 9 exit-code file | `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865` |
| Final OptiX 8 preflight v2 JSON | `9f87eab8d383b0fe56a70431bdef1bfc09dbeb03ff4da8bd493cb0c002185e32` |
| Final OptiX 8 native manifest | `679b0db35c64afc554d4095300a1431d99772ffb5bf211e7635572ba718e04cb` |
| Final OptiX 8 native build log | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| Final OptiX 8 complete GPU result | `59e50a9f121f13b5b32fc13f2c9f6550a6756a3b48ad1a065fe824c60a93463f` |

The five v1 rows are preserved inside the initial diagnostic bundle. The six
final rows are preserved both as standalone files and inside the controlling
final bundle; the standalone checksum manifest verifies all six.

All native build logs are empty files with the SHA-256 of empty bytes because
the successful builder emitted no compiler diagnostics.

## Remaining separate gates

1. Perform the owner-deferred external review before consensus or public
   promotion wording.
2. Preregister an Embree/timing protocol before benchmark or speedup claims.
3. Use R570-or-newer hardware only if separate OptiX 9 coverage is desired.
