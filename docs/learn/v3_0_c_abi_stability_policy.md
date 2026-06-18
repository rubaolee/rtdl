# V3.0 C ABI Stability Policy

Status: draft policy for the V3 embeddability track. The current C ABI is
versioned as `0.1.2`, source-tree only, and not frozen.

This page defines what the current C ABI does and does not promise while RTDL
moves from a proof boundary toward a stable embedding contract.

## Current State

- Public header: `include/rtdl/rtdl.h`.
- Build target: `make build-c-api`.
- Current library source: `src/native/rtdl_c_api.cpp`.
- Draft symbol manifest:
  [`v3_0_c_abi_symbol_manifest_v0_1_2.json`](v3_0_c_abi_symbol_manifest_v0_1_2.json).
- Ownership/threading contract:
  [`v3_0_c_abi_ownership_threading_contract.md`](v3_0_c_abi_ownership_threading_contract.md).
- Current validated route: host `F32` AABB2 overlap returning host `U64`
  `(query_id, primitive_id)` pairs.
- Current evidence gates: header compile, shared-library build, exported-symbol
  audit, non-Python C client, negative runtime cases, source-tree doctor, and
  `v3_current`.

The ABI version remains `0.x`; external users should treat it as an experimental
source-tree boundary.

## Current Draft Compatibility Rule

The current library exposes `rtdl_abi_is_compatible(major, minor, patch)` so
embedding clients can fail closed before using a mismatched header/library pair.
For the `0.1.2` draft, compatibility means:

- `major == RTDL_ABI_VERSION_MAJOR`.
- `minor == RTDL_ABI_VERSION_MINOR`.
- `patch <= RTDL_ABI_VERSION_PATCH`.

Descriptor entrypoints currently carry major/minor fields only, so
`rtdl_context_create`, `rtdl_index_build`, and `rtdl_query_execute` reject
descriptor major/minor values that do not match the library. This is a draft
guardrail, not a stable 1.0 compatibility promise.

## What Is Allowed Before 1.0

Before a `1.0` ABI, RTDL may make breaking changes when they are needed to fix
the boundary. Every breaking change must:

- Update `RTDL_ABI_VERSION_*` in the public header when the C shape or semantics
  change.
- Refresh the C ABI draft, embedding example docs, source-tree doctor evidence,
  and `v3_current` matrix.
- Keep unsupported routes fail-closed rather than silently accepting inputs with
  undefined behavior.
- Preserve explicit ownership rules for caller-retained, release-callback, and
  RTDL-owned buffers.

No 0.x artifact authorizes packaged SDK wording, binary compatibility promises,
or downstream language binding stability.

## 1.0 Freeze Requirements

RTDL may call the C ABI stable only after all of these are true:

- A symbol manifest is checked and versioned as part of release evidence.
- Cross-version compatibility tests prove that an older C client still loads and
  runs against the newer shared library for the supported symbol set.
- The public header documents every stable struct, enum, status code, ownership
  rule, and thread-safety rule.
- At least one non-Python client validates a real query route.
- Negative runtime tests cover invalid dtype, device, ABI version, unsupported
  primitive/query kinds, and empty-result behavior.
- Package/install instructions exist for at least one supported platform.
- OptiX/Embree/device-buffer routes are either implemented and tested or
  explicitly excluded from the stable surface.

Until those gates pass, public wording must say draft, source-tree, or
experimental, never stable SDK.

## Future Compatibility Rules

After `1.0`, stable releases should follow these rules:

- Opaque handle layouts remain private; callers never depend on struct layout.
- Existing exported C symbols are not removed inside a major version.
- Enum values and status codes are not reused for different meanings.
- New functions, enum values, and optional capabilities may be added in minor
  versions.
- Behavior changes that can break existing clients require a major version
  change or an explicit opt-in capability flag.
- C++ types, exceptions, STL containers, CUDA/OptiX internals, and app-specific
  structs never cross the public C boundary.

## Boundary

This policy does not itself freeze the ABI, build a package, implement DLPack,
authorize external stream semantics, implement OptiX/Embree C ABI queries, or
make performance claims. It is the rulebook for deciding when those claims
become possible.
