# V3.0 C ABI Staging Contract

Status: historical V3-track file retained as V4.0 preparatory material. This
draft source-tree staging contract is not V3.0 release scope, not a V3.0
completion criterion, and not a packaged SDK, installer, stable ABI, or release
artifact.

Run this from the repository root:

```bash
make stage-c-api
```

The target first builds `build/librtdl_c_api.*`, then creates
`build/c_api_stage` with:

- `include/rtdl/rtdl.h`
- `lib/librtdl_c_api.*`
- `lib/pkgconfig/rtdl-c-api.pc`
- `lib/cmake/rtdl-c-api/rtdl-c-api-config.cmake`
- `share/rtdl/v3_0_c_abi_symbol_manifest.json`
- `share/rtdl/README.md`
- `examples/c_api_aabb2_overlap_client.c`
- `examples/c_api_direct_link_client.c`
- `examples/c_api_host_runtime_client.c`
- `examples/c_api_cuda_buffer_metadata_client.c`
- `examples/c_api_last_error_client.c`
- `examples/python_ctypes_client.py`
- `examples/python_ctypes_aabb2_query_client.py`
- `examples/python_ctypes_cuda_buffer_metadata_client.py`
- `examples/python_ctypes_dlpack_like_metadata_client.py`

The staged manifest is copied from the current draft source-tree manifest,
currently `docs/learn/v3_0_c_abi_symbol_manifest_v0_1_3.json`.

To create a movable archive of the same source-tree stage:

```bash
make package-c-api-stage
```

This writes `build/rtdl-c-api-stage-0.1.3.tar.gz`. The archive is a convenient
source-tree staging package, not a system install, package-manager artifact, or
stable SDK.

To create a DESTDIR/prefix-style layout that external projects can consume with
ordinary `pkg-config` paths:

```bash
make stage-c-api-prefix
```

By default this writes:

- `build/c_api_prefix_stage/usr/local/include/rtdl/rtdl.h`
- `build/c_api_prefix_stage/usr/local/lib/librtdl_c_api.*`
- `build/c_api_prefix_stage/usr/local/lib/pkgconfig/rtdl-c-api.pc`
- `build/c_api_prefix_stage/usr/local/lib/cmake/rtdl-c-api/rtdl-c-api-config.cmake`
- `build/c_api_prefix_stage/usr/local/share/rtdl/v3_0_c_abi_symbol_manifest.json`
- `build/c_api_prefix_stage/usr/local/share/rtdl/README.md`
- `build/c_api_prefix_stage/usr/local/share/rtdl/examples/*`

The stage root and prefix are configurable:

```bash
make stage-c-api-prefix C_API_PREFIX_STAGE_ROOT=/tmp/rtdl-stage C_API_PREFIX=/opt/rtdl
```

This is a prefix-layout staging proof only. It verifies that the staged header,
library, examples, and relocatable `pkg-config` metadata work after being placed
under a conventional prefix. It is not a privileged system install, package
manager artifact, stable SDK, or release claim.

## Example

On Linux/pod, after `make stage-c-api`:

```bash
cc -std=c11 -I build/c_api_stage/include \
  build/c_api_stage/examples/c_api_aabb2_overlap_client.c \
  -o build/c_api_stage/examples/rtdl_c_api_aabb2_overlap_client \
  -ldl
./build/c_api_stage/examples/rtdl_c_api_aabb2_overlap_client \
  build/c_api_stage/lib/librtdl_c_api.so
```

Expected output:

```text
hit_count=1 first_pair=(0,0)
```

For direct-link C clients that want compile/link flags from the staged bundle:

```bash
export PKG_CONFIG_PATH="$PWD/build/c_api_stage/lib/pkgconfig"
pkg-config --cflags --libs rtdl-c-api
cc -std=c11 $(pkg-config --cflags rtdl-c-api) \
  build/c_api_stage/examples/c_api_direct_link_client.c \
  -o build/c_api_stage/examples/rtdl_c_api_direct_link_client \
  $(pkg-config --libs rtdl-c-api)
LD_LIBRARY_PATH="$PWD/build/c_api_stage/lib:${LD_LIBRARY_PATH:-}" \
  ./build/c_api_stage/examples/rtdl_c_api_direct_link_client
```

For the prefix-style stage:

```bash
make stage-c-api-prefix
export PKG_CONFIG_PATH="$PWD/build/c_api_prefix_stage/usr/local/lib/pkgconfig"
cc -std=c11 $(pkg-config --cflags rtdl-c-api) \
  build/c_api_prefix_stage/usr/local/share/rtdl/examples/c_api_direct_link_client.c \
  -o build/c_api_prefix_stage/usr/local/share/rtdl/examples/rtdl_c_api_direct_link_client \
  $(pkg-config --libs rtdl-c-api)
LD_LIBRARY_PATH="$PWD/build/c_api_prefix_stage/usr/local/lib:${LD_LIBRARY_PATH:-}" \
  ./build/c_api_prefix_stage/usr/local/share/rtdl/examples/rtdl_c_api_direct_link_client
```

Expected output:

```text
direct_link_ok 0.1.3 ok
```

The same prefix-style stage also carries Python `ctypes` examples:

```bash
python3 build/c_api_prefix_stage/usr/local/share/rtdl/examples/python_ctypes_client.py \
  build/c_api_prefix_stage/usr/local/lib/librtdl_c_api.so
python3 build/c_api_prefix_stage/usr/local/share/rtdl/examples/python_ctypes_aabb2_query_client.py \
  build/c_api_prefix_stage/usr/local/lib/librtdl_c_api.so
python3 build/c_api_prefix_stage/usr/local/share/rtdl/examples/python_ctypes_cuda_buffer_metadata_client.py \
  build/c_api_prefix_stage/usr/local/lib/librtdl_c_api.so
python3 build/c_api_prefix_stage/usr/local/share/rtdl/examples/python_ctypes_dlpack_like_metadata_client.py \
  build/c_api_prefix_stage/usr/local/lib/librtdl_c_api.so
```

Expected outputs include:

```text
python_ctypes_ok 0.1.3 ok
python_ctypes_hit_count=1 first_pair=(0,0)
python_ctypes_cuda_metadata_shape=(3,4) query_route_rejected=invalid argument
python_ctypes_dlpack_like_metadata_shape=(2,3) query_route_rejected=invalid argument
```

For an external CMake project:

```cmake
cmake_minimum_required(VERSION 3.16)
project(rtdl_c_api_consumer C)
find_package(rtdl-c-api CONFIG REQUIRED)
add_executable(consumer main.c)
target_link_libraries(consumer PRIVATE rtdl::c_api)
```

Configure with the staged prefix:

```bash
cmake -S . -B build -DCMAKE_PREFIX_PATH="$PWD/build/c_api_prefix_stage/usr/local"
cmake --build build
```

For a CMake consumer from the extracted source-tree archive:

```bash
make package-c-api-stage
mkdir -p /tmp/rtdl-c-api-consume
tar -C /tmp/rtdl-c-api-consume -xzf build/rtdl-c-api-stage-0.1.3.tar.gz
cmake -S . -B build -DCMAKE_PREFIX_PATH="/tmp/rtdl-c-api-consume/rtdl-c-api-stage-0.1.3"
cmake --build build
```

The extracted source-tree archive carries runnable C examples too:

```bash
export RTDL_C_API_ARCHIVE=/tmp/rtdl-c-api-consume/rtdl-c-api-stage-0.1.3
export PKG_CONFIG_PATH="$RTDL_C_API_ARCHIVE/lib/pkgconfig"
cc -std=c11 $(pkg-config --cflags rtdl-c-api) \
  "$RTDL_C_API_ARCHIVE/examples/c_api_direct_link_client.c" \
  -o "$RTDL_C_API_ARCHIVE/examples/rtdl_c_api_direct_link_client" \
  $(pkg-config --libs rtdl-c-api)
LD_LIBRARY_PATH="$RTDL_C_API_ARCHIVE/lib:${LD_LIBRARY_PATH:-}" \
  "$RTDL_C_API_ARCHIVE/examples/rtdl_c_api_direct_link_client"
```

Additional extracted-archive C examples validate the `dlopen` host AABB2
route, host external-runtime metadata, CUDA descriptor metadata, and
status/last-error diagnostics. Expected outputs include:

```text
direct_link_ok 0.1.3 ok
hit_count=1 first_pair=(0,0)
validated_host_external_runtime_cases=3
validated_cuda_buffer_metadata_cases=4
validated_last_error_diagnostics_cases=7
```

The extracted source-tree archive also carries the Python `ctypes` examples:

```bash
python3 /tmp/rtdl-c-api-consume/rtdl-c-api-stage-0.1.3/examples/python_ctypes_client.py \
  /tmp/rtdl-c-api-consume/rtdl-c-api-stage-0.1.3/lib/librtdl_c_api.so
python3 /tmp/rtdl-c-api-consume/rtdl-c-api-stage-0.1.3/examples/python_ctypes_aabb2_query_client.py \
  /tmp/rtdl-c-api-consume/rtdl-c-api-stage-0.1.3/lib/librtdl_c_api.so
python3 /tmp/rtdl-c-api-consume/rtdl-c-api-stage-0.1.3/examples/python_ctypes_cuda_buffer_metadata_client.py \
  /tmp/rtdl-c-api-consume/rtdl-c-api-stage-0.1.3/lib/librtdl_c_api.so
python3 /tmp/rtdl-c-api-consume/rtdl-c-api-stage-0.1.3/examples/python_ctypes_dlpack_like_metadata_client.py \
  /tmp/rtdl-c-api-consume/rtdl-c-api-stage-0.1.3/lib/librtdl_c_api.so
```

Expected outputs include:

```text
python_ctypes_ok 0.1.3 ok
python_ctypes_hit_count=1 first_pair=(0,0)
python_ctypes_cuda_metadata_shape=(3,4) query_route_rejected=invalid argument
python_ctypes_dlpack_like_metadata_shape=(2,3) query_route_rejected=invalid argument
```

For a C client that validates the current host external-runtime metadata path:

```bash
cc -std=c11 $(pkg-config --cflags rtdl-c-api) \
  build/c_api_stage/examples/c_api_host_runtime_client.c \
  -o build/c_api_stage/examples/rtdl_c_api_host_runtime_client \
  $(pkg-config --libs rtdl-c-api)
LD_LIBRARY_PATH="$PWD/build/c_api_stage/lib:${LD_LIBRARY_PATH:-}" \
  ./build/c_api_stage/examples/rtdl_c_api_host_runtime_client
```

Expected output includes:

```text
validated_host_external_runtime_cases=3
```

For a C client that validates CUDA buffer metadata import/export without
executing a CUDA query route:

```bash
cc -std=c11 $(pkg-config --cflags rtdl-c-api) \
  build/c_api_stage/examples/c_api_cuda_buffer_metadata_client.c \
  -o build/c_api_stage/examples/rtdl_c_api_cuda_buffer_metadata_client \
  $(pkg-config --libs rtdl-c-api)
LD_LIBRARY_PATH="$PWD/build/c_api_stage/lib:${LD_LIBRARY_PATH:-}" \
  ./build/c_api_stage/examples/rtdl_c_api_cuda_buffer_metadata_client
```

Expected output includes:

```text
validated_cuda_buffer_metadata_cases=4
```

For a Python `ctypes` client that maps a `__cuda_array_interface__`-style
descriptor into the C ABI neutral buffer view:

```bash
python3 build/c_api_stage/examples/python_ctypes_cuda_buffer_metadata_client.py \
  build/c_api_stage/lib/librtdl_c_api.so
```

Expected output:

```text
python_ctypes_cuda_metadata_shape=(3,4) query_route_rejected=invalid argument
```

For a Python `ctypes` client that maps a DLPack-like producer object with
explicit dtype, shape, device, and pointer metadata into the C ABI neutral
buffer view:

```bash
python3 build/c_api_stage/examples/python_ctypes_dlpack_like_metadata_client.py \
  build/c_api_stage/lib/librtdl_c_api.so
```

Expected output:

```text
python_ctypes_dlpack_like_metadata_shape=(2,3) query_route_rejected=invalid argument
```

For a minimal Python `ctypes` client over the same staged shared library:

```bash
python3 build/c_api_stage/examples/python_ctypes_client.py \
  build/c_api_stage/lib/librtdl_c_api.so
```

Expected output:

```text
python_ctypes_ok 0.1.3 ok
```

For the same Python `ctypes` path running a host AABB2 overlap query:

```bash
python3 build/c_api_stage/examples/python_ctypes_aabb2_query_client.py \
  build/c_api_stage/lib/librtdl_c_api.so
```

Expected output:

```text
python_ctypes_hit_count=1 first_pair=(0,0)
```

## Boundary

- This is a source-tree staging bundle only.
- `package-c-api-stage` archives that staging bundle for movement between
  directories and carries the staged `pkg-config` and CMake metadata; it is
  still not an installed SDK. The archive-stage Python smoke validates that the
  same thin Python `ctypes` examples can run from an extracted archive without
  source-tree relative paths; the archive-stage C examples smoke validates the
  extracted C examples the same way.
- `stage-c-api-prefix` creates a DESTDIR/prefix-style staging layout; it is
  still not a privileged system install, package manager artifact, stable SDK,
  or release claim.
- The only validated route remains host `F32` AABB2 overlap through the draft C
  ABI.
- The Python `ctypes` example validates only thin shared-library loading,
  version/capability queries, and context lifecycle calls.
- The Python `ctypes` AABB2 query example validates the current host buffer
  import, index build, query execute, result export, and cleanup path only.
- The C host-runtime example validates host runtime metadata only; CUDA,
  external stream, OptiX, and Embree runtime adoption remain fail-closed.
- The CUDA buffer metadata example validates neutral descriptor import/export
  and release-callback behavior only; CUDA query execution, external stream
  ordering, and public true-zero-copy wording remain fail-closed.
- The Python `ctypes` CUDA metadata example validates a
  `__cuda_array_interface__`-style descriptor bridge into the C ABI only; it
  does not validate CUDA pointer ownership, stream ordering, or device
  execution.
- The Python `ctypes` DLPack-like metadata example validates a DLPack-like
  producer object with explicit dtype/shape/pointer metadata into the C ABI
  only; it does not parse arbitrary DLPack capsules, validate CUDA pointer
  ownership, stream ordering, or device execution.
- No install prefix, package manager artifact, Python wheel, stable binary
  compatibility, OptiX/Embree C ABI query, device-buffer query route, or
  performance wording is authorized.
