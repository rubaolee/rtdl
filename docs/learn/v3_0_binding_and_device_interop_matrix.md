# V3.0 Binding And Device Interop Matrix

Status: current V3 source-tree evidence matrix, not a stable SDK, generated
binding package, device-buffer query route, or public true-zero-copy claim.

This page is the short map for what an external program can do with the current
V3 draft C ABI and where the boundary still stops. It consolidates the C,
Python `ctypes`, staging, CUDA metadata, and future interop contracts so a user
does not confuse descriptor metadata with executable device memory support.

## Current Matrix

| Surface | Current Status | Evidence Role | Boundary |
| --- | --- | --- | --- |
| C dynamic-load client | Validated source-tree example. | Loads `librtdl_c_api`, checks version/status/context lifecycle, and runs the host AABB2 route in the current examples. | Not a frozen ABI or installed SDK. |
| C direct-link client | Validated source-tree and staged handoff example. | Uses staged header/library metadata through direct linking. | Still source-tree staging, not package-manager install. |
| C examples from archive stage | Validated extracted-archive smoke. | Compiles and runs direct-link, `dlopen` host AABB2, host-runtime metadata, and CUDA descriptor metadata examples from the unpacked archive. | Source-tree archive evidence only, not a packaged SDK. |
| `pkg-config` stage | Validated source-tree and prefix-stage handoff. | External C clients can obtain include and library flags from the staged `.pc` file. | Does not imply system install or binary compatibility. |
| CMake prefix/archive package | Validated prefix and extracted archive handoff. | External CMake consumers can `find_package(rtdl-c-api CONFIG REQUIRED)` against staged artifacts. | Staged CMake metadata only, not a released SDK. |
| Python `ctypes` lifecycle client | Validated thin language-binding style example. | Loads the shared library and checks version/capability/context lifecycle without writing C. | Not a generated Python package or complete binding. |
| Python `ctypes` host AABB2 query | Validated current query-route example. | Imports host buffers, builds a host AABB2 index, executes overlap query, exports host result rows, and cleans up handles. | Host F32 AABB2 to host U64 pairs only. |
| Python `ctypes` examples from archive stage | Validated extracted-archive smoke. | Runs lifecycle, host AABB2, CUDA metadata, and DLPack-like metadata examples from the unpacked `rtdl-c-api-stage-0.1.3` archive. | Source-tree archive evidence only, not a Python wheel or installed SDK. |
| Host external runtime metadata | Validated fail-closed metadata route. | Accepts host runtime metadata and rejects malformed/CUDA runtime handles. | No external CUDA stream adoption. |
| Independent-context host-route concurrency | Validated source-tree smoke. | Runs the current host AABB2 route concurrently through independent contexts with no shared handles. | Not a stable thread-safety guarantee, and shared-handle concurrency still requires external synchronization. |
| CUDA buffer descriptor import/export | Validated metadata-only C route. | Preserves pointer, dtype, shape, strides, device id, and release callback without dereferencing the pointer. | No CUDA pointer ownership proof, no stream ordering proof, no device-buffer query execution. |
| `__cuda_array_interface__` to C ABI descriptor | Validated metadata-only Python bridge. | Python `ctypes` can translate a CUDA-array-interface style object into the neutral C ABI buffer descriptor. | The resulting CUDA descriptor is rejected by the current host query route. |
| DLPack-like object to C ABI descriptor | Validated metadata-only Python bridge. | Python `ctypes` can translate a DLPack-like producer object with explicit dtype, shape, device, and pointer metadata into the neutral C ABI buffer descriptor. | It does not parse arbitrary DLPack capsules, validate ownership, synchronize streams, or execute device-buffer query routes. |
| DLPack | Validated protocol classification/descriptor gate; runtime still blocked. | The neutral-buffer seam can classify DLPack-like objects and produce descriptor metadata in synthetic tests. | No implemented C ABI DLPack adapter, device-buffer route, external stream ordering, or true-zero-copy proof. |
| Device-buffer query route | Blocked. | Future runtime target. | No current C ABI query route consumes CUDA/HIP/Metal/Vulkan buffers. |
| External CUDA stream ordering | Blocked. | Future runtime target. | No same-stream/event/transfer-counter proof at the C ABI boundary. |
| Generated language bindings | Blocked. | Future packaging target. | Current Python examples are hand-written `ctypes` examples only. |

## Required Wording

- Say "source-tree/staged C ABI examples" for the current C and Python
  `ctypes` evidence, including extracted source-tree archive examples.
- Say "CUDA descriptor metadata" or "metadata-only CUDA buffer descriptor" for
  the current CUDA pointer handoff.
- Say "DLPack-like descriptor metadata" for the current Python `ctypes`
  DLPack-like bridge.
- Do not say DLPack support, true zero-copy support, device-resident query
  route, external CUDA stream adoption, generated bindings, packaged SDK,
  stable ABI, release, or performance claim based only on this matrix.

## Relationship To Other V3 Docs

- [V3.0 C ABI Draft](v3_0_c_abi_draft.md) defines the current public header and
  host AABB2 query route.
- [V3.0 C ABI Staging Contract](v3_0_c_abi_staging_contract.md) defines the
  source-tree, prefix, archive, pkg-config, and CMake handoff shapes.
- [V3.0 Zero-Copy Interop Contract](v3_0_zero_copy_interop_contract.md) defines
  the future proof requirements before any public true-zero-copy wording.
- [V3.0 Toolchain Support Matrix](v3_0_toolchain_support_matrix.md) records the
  current pod-side toolchain observations used by the evidence reports.
