# Bounded linear RT-CCD owner-grouped core

## Scope

This successor case study implements a paper-derived subset of linear robot
trajectory collision detection. Constant-radius swept-sphere path segments are
OptiX round-linear curves. Finite directed obstacle edges are ray queries. A
generic RTDL any-hit primitive maps every accepted curve primitive to an
application-provided owner and performs device-side Boolean OR into one bit per
trajectory.

The result answers: **which candidate trajectories intersect at least one
queried obstacle edge?** Multiple path segments and spheres may belong to the
same trajectory owner.

## Boundary

Application code owns:

- trajectory, sphere, path-segment, and directed-edge identities;
- primitive-to-trajectory owner mapping;
- directed obstacle-edge construction;
- collision interpretation; and
- the independent finite segment/capsule oracle.

The RTDL engine owns only the app-neutral contract:

```text
accepted event = (query_id, primitive_id)
owner = owner_ids[primitive_id]
owner_hit_bits[owner] |= 1
continue traversal
```

The callback language already expresses any-hit continuation. The new work is
a generic physical lowering and standard-library operation, analogous to adding
a necessary library primitive rather than repairing a fundamental inability of
the language.

## Directed-edge policy

The frozen Goal5835 projection selected one arbitrary direction per deduplicated
mesh edge and therefore did not preserve the author method's inside-start
contract. This successor requires directed edges explicitly. Its deterministic
fixtures conservatively expand each undirected test edge into both directions;
that app policy is stronger and more expensive than choosing one direction, but
it does not put mesh orientation logic into the engine.

This is not a claim that the author mesh-loop preprocessing has been reproduced.

## Deliberate subset

Included:

- piecewise-linear constant-radius swept spheres;
- multiple trajectory owners and multiple primitives per owner;
- finite directed obstacle-edge queries;
- per-trajectory Boolean collision decisions;
- duplicate/order-invariant any-hit reduction; and
- start-inside local fixtures with bidirectional query edges.
- a cheap O(P+Q) surface-crossing admission requiring every finite query edge
  to be longer than every individual capsule diameter.

Excluded:

- full Franka/62-sphere benchmark reconstruction;
- arbitrary robot kinematics and continuous rotational interpolation;
- face-interior collision without an edge/curve intersection;
- query edges wholly contained in one swept capsule;
- tangent and near-tangent inputs outside the registered numeric gap;
- time of impact, contact points, normals, and hit counts;
- author-code performance comparison; and
- any public performance or paper-reproduction claim.

## Evidence state

Local deterministic tests establish app mapping, reusable prepared execution,
CPU oracle behavior, schema/source determinism, six semantic boundary cases,
three scale ladders, and engine/app separation. The checked-in receipt still
records zero GPU launches.

A separate internal Pod diagnostic at commit `2c48337` used official OptiX 8
headers on an RTX 4000 Ada GPU and passed all nine workloads twice: 18 true
OptiX launches, 18 matching GPU executions, independent-oracle parity, and
prepared reuse. That run does not satisfy the pinned OptiX 9 formal gate and
registers no performance samples. See
`history/internal_docs/successor_owner_grouped_pod_20260902/INTERNAL_POD_DIAGNOSTIC_REPORT.md`.

The length admission is a sufficient, deliberately conservative subset rule.
It prevents the logical case where a finite edge lies wholly inside a capsule
and therefore intersects the volume without crossing the OptiX curve surface.
It is evaluated over canonical-f32 inputs using an outward-rounded query-length
lower bound and capsule-diameter upper bound. It does not perform pairwise
collision discovery; the registered workload oracle separately verifies a
nonzero surface-distance gap. Arbitrary near-boundary inputs are outside the
current claim; every registered pair is at least `2^-10` away from the
capsule-radius boundary under the independent distance oracle.

The current handoff snapshot has no root `Makefile`. On a compatible NVIDIA
host, first run the fail-fast toolchain preflight. It compiles a minimal
`nvcc`/host-compiler object plus the exact four restricted-Python/Numba
callback leaves and trusted NVRTC wrapper. A separate temporary `optixInit()`
probe requires the selected SDK ABI to negotiate with the host driver. It
builds no RTDL native library and launches no OptiX work:

```bash
PYTHONPATH=src:. python scripts/successor_owner_grouped_pod_preflight.py \
  --cuda-prefix /usr/local/cuda \
  --optix-prefix /path/to/optix \
  --expected-optix-sdk 9.0.0 \
  --compute-capability 8.9 \
  --output /tmp/owner_grouped_preflight.json
```

Then build a fresh native library with the explicit builder:

```bash
PYTHONPATH=src:. python scripts/build_v4_optix_native_snapshot.py \
  --cuda-prefix /usr/local/cuda \
  --optix-prefix /path/to/optix \
  --expected-optix-sdk 9.0.0 \
  --compute-capability 8.9 \
  --output build/librtdl_optix.so \
  --manifest /tmp/owner_grouped_native_build.json \
  --log /tmp/owner_grouped_native_build.log
```

Then run every registered semantic and scale workload through the public app
front door:

```bash
PYTHONPATH=src:. python \
  scripts/successor_linear_rtccd_owner_grouped_pod_runner.py \
  --native build/librtdl_optix.so \
  --native-manifest /tmp/owner_grouped_native_build.json \
  --optix-prefix /path/to/optix \
  --cuda-prefix /usr/local/cuda \
  --optix-include /path/to/optix/include \
  --cuda-include /usr/local/cuda/include \
  --optix-sdk 9.0.0 \
  --compute-capability 8.9 \
  --repeat 2 \
  --artifact-dir /tmp/owner_grouped_artifacts \
  --output /tmp/owner_grouped_gpu_result.json
```

Native OptiX 8 compilation and bounded diagnostic traversal parity now exist;
the registered OptiX 9 formal route remains unproven until that runner passes
on a driver-compatible Pod.
The runner rejects a native library that is not bound by the supplied build
manifest to the same Git commit, builder bytes, exact `nvcc` and host compiler,
GPU UUID/driver/compute capability, complete native source inventory, and
complete CUDA/OptiX header inventories. It separately binds the exact
NVRTC/NVVM/libdevice files used at runtime. The preflight and runner configure
the CUDA loader/compiler environment before compilation and disable ambient
formal-leaf caches. Nonstandard runtime-library locations can be supplied with
`--nvrtc-library`, `--nvvm-library`, and `--libdevice` to both commands. The
builder accepts `--host-compiler` when the default `g++` is not the intended
CUDA-compatible compiler. The runner also rejects toolchain or source drift
during the run and leaves an explicit `RUN_INCOMPLETE.json` marker if
validation aborts before a complete result. Its nanosecond fields are
diagnostics, not registered benchmark samples. This is not yet a completed
benchmark app and author-code/performance claims remain excluded.
