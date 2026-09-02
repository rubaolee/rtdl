# Successor owner-grouped OptiX functional-profile decision

Date: 2026-09-02

Decision class: owner-directed internal engineering decision

Status: `OPTIX_8_0_INTERNAL_GPU_FUNCTIONAL_PROFILE_ACCEPTED`

External review count: 0; review remains owner-deferred while traveling

## Decision

OptiX 8.0.0 on the exact RTX 4000 Ada/R550 Pod is the registered internal GPU
functional-validation profile for the successor `OWNER_GROUPED_ANY_HIT /
BOOL_OR` primitive and bounded linear RT-CCD case study.

OptiX 9 is additional provider-version coverage, not a prerequisite for this
primitive's functional completion. This decision does not claim that OptiX 9
runs on R550, does not reinterpret OptiX 8 bytes as OptiX 9 bytes, and does not
authorize performance or public promotion wording.

## Why this is not a semantic downgrade

No frozen successor authority preregistered OptiX 9 as the only acceptable
provider profile. The earlier 9.0.0 selection was a CLI/documentation default,
not an application, language, primitive, or native-ABI requirement.

Static inspection and the successful OptiX 8 build show that this route uses:

- `OPTIX_BUILD_INPUT_TYPE_CURVES` with
  `OPTIX_PRIMITIVE_TYPE_ROUND_LINEAR`;
- one static GAS and one built-in curve intersection module;
- `optixTrace`, an any-hit program, `atomicOr`, and
  `optixIgnoreIntersection`;
- the same four restricted-Python callback leaves and trusted wrapper; and
- no OptiX 9 cluster, cooperative-vector, Blackwell-only linear-curve, or other
  OptiX 9-specific API.

The version remains part of `CurveTargetProfile`, build manifests, runtime
descriptors, PTX materialization, and result artifacts. Evidence from one
version cannot satisfy another version's identity checks.

## Compatibility evidence

NVIDIA's official legacy-download page states that OptiX 8.0 requires an R535
or newer driver, while OptiX 9.0 requires R570 or newer:

- <https://developer.nvidia.com/designworks/optix/downloads/legacy>
- <https://forums.developer.nvidia.com/t/optix-9-0-release/322842>

The provided Pod has driver 550.127.05. Therefore:

- OptiX 8.0 is an officially supported pairing and `optixInit()` returned 0;
- OptiX 9.0 is below its official driver floor and returned
  `OPTIX_ERROR_UNSUPPORTED_ABI_VERSION` (7801); and
- injecting an R570 `libnvoptix` into an R550 container would be an unsupported
  mixed-driver experiment, not acceptable formal evidence.

## Completed internal functional gate

At clean commit `5ee0e9404a1262decca6176642edc9f764d8c3f3`:

- preflight v2 bound OptiX 8.0.0, CUDA 12.8, compute capability 8.9, exact
  compiler/runtime libraries, SDK headers, GPU UUID, and driver;
- the runtime ABI probe returned `optixInit_result=0` with zero launches;
- a fresh native library exported all four required C ABI symbols;
- the public app front door passed six semantic plus three scale workloads,
  repeated twice, for 18/18 true-OptiX launches and oracle matches; and
- an additional near-runner-limit scale used 512 owners, 4096 primitives, and
  1024 queries. Its oracle evaluated 4,194,304 primitive/query pairs; all three
  prepared GPU executions matched, bringing that run to 21/21 launches.

The exact artifacts and hashes are recorded in
`successor_owner_grouped_pod_20260902/INTERNAL_POD_DIAGNOSTIC_REPORT.md`.

## Remaining boundaries

- This closes the internal GPU functional gate for the bounded app and generic
  primitive on the exact OptiX 8 profile.
- It does not make the app a complete reproduction of the author benchmark.
- It does not establish an Embree comparison or performance result.
- It does not prove OptiX 9 portability.
- It does not provide external review or consensus.

Future OptiX 9 execution is useful environment-diversity coverage, but it is
not a reason to keep this version-independent primitive implementation open.
Performance study, broader app promotion, and external review remain separate
explicit gates.
