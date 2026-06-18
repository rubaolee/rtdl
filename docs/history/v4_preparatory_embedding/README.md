# V4 Preparatory Embedding Archive

This directory preserves embedding, C ABI, SDK-staging, generated-binding,
device-buffer, external-runtime, zero-copy, and interop preparation artifacts.
They are historical or preparatory evidence only.

V3.0 excludes embedding/SDK/zero-copy work. Those items are V4.0 scope.

## What Is Here

- [V3.0 Embeddability Architecture Strategy](v3_0_embeddability_architecture_strategy.md).
- [V3.0 C ABI Draft](v3_0_c_abi_draft.md).
- [V3.0 C ABI Stability Policy](v3_0_c_abi_stability_policy.md).
- [V3.0 C ABI Ownership And Threading Contract](v3_0_c_abi_ownership_threading_contract.md).
- [V3.0 C ABI Staging Contract](v3_0_c_abi_staging_contract.md).
- [V3.0 Zero-Copy Interop Contract](v3_0_zero_copy_interop_contract.md).
- [V3.0 Toolchain Support Matrix](v3_0_toolchain_support_matrix.md).
- [V3.0 Binding And Device Interop Matrix](v3_0_binding_and_device_interop_matrix.md).
- Symbol manifests from the preparatory C ABI work.
- Archived draft C ABI staging inputs under [staging](staging/README.md),
  including the draft header, pkg-config metadata, and CMake metadata.
- Source-tree C/Python embedding examples under [examples/embedding](examples/embedding/README.md).

## Reading Rule

Read these files only when investigating V4 planning or historical scope drift.
They do not define V3.0 completion, do not authorize V3.0 release wording, and
do not make V3.0 an SDK or embeddability release.
