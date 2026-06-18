# RTDL C ABI Embedding Examples

Status: V3 draft source-tree examples.

These examples show how a non-Python program can load the draft RTDL C ABI
library from the source tree. They are not a packaged SDK, frozen ABI, or
release contract.

## Host AABB2 Overlap

The first example builds a host `F32` AABB2 index, runs one host AABB overlap
query, and reads a host `U64` `(query_id, primitive_id)` pair buffer.

Current data contract:

- Primitive and query buffers are host `RTDL_DTYPE_F32` AABB2 rows shaped
  `[count, 4]` as `(min_x, min_y, max_x, max_y)`.
- The result buffer is host `RTDL_DTYPE_U64`, shaped `[hit_count, 2]`, with
  rows `(query_id, primitive_id)`.
- For the current host AABB2 route, rows are deterministic: ascending
  `query_id`, then ascending `primitive_id` within each query.
- `rtdl_index_build` copies primitive coordinates into the index; imported
  buffers are caller-retained when `release == NULL` and release-callback-owned
  by the buffer handle when `release != NULL`. Query result buffers are
  RTDL-owned and must be released with `rtdl_buffer_destroy`.

Linux/pod commands from the repository root:

```bash
make build-c-api
cc -std=c11 -I include \
  examples/current/embedding/c_api_aabb2_overlap_client.c \
  -o build/rtdl_c_api_aabb2_overlap_client \
  -ldl
./build/rtdl_c_api_aabb2_overlap_client build/librtdl_c_api.so
```

Expected output:

```text
hit_count=1 first_pair=(0,0)
```

## Source-Tree Staging Bundle

For a cleaner non-Python handoff, use:

```bash
make stage-c-api
```

This creates `build/c_api_stage` with the public header, shared library, current
draft symbol manifest, `lib/pkgconfig/rtdl-c-api.pc`, this README, the AABB2
dlopen and direct-link C examples, C host-runtime metadata and CUDA
buffer-metadata examples, a thin Python `ctypes` lifecycle example, Python
`ctypes` host AABB2 query example, and Python `ctypes` CUDA buffer-metadata
example. It is still a source-tree staging bundle, not an installed SDK.

To archive that same movable source-tree stage:

```bash
make package-c-api-stage
```

This writes `build/rtdl-c-api-stage-0.1.3.tar.gz`.

For a prefix-style stage that external projects can consume without relying on
the repository layout:

```bash
make stage-c-api-prefix
```

By default this writes the C ABI header, shared library, pkg-config metadata,
CMake package config, manifest, README, and examples under
`build/c_api_prefix_stage/usr/local`. The root and prefix can be overridden:

```bash
make stage-c-api-prefix C_API_PREFIX_STAGE_ROOT=/tmp/rtdl-stage C_API_PREFIX=/opt/rtdl
```

For direct-link clients from that prefix-style stage:

```bash
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

The same prefix-style stage can run the Python `ctypes` examples without using
source-tree relative paths:

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

Configure with:

```bash
cmake -S . -B build -DCMAKE_PREFIX_PATH="$PWD/build/c_api_prefix_stage/usr/local"
cmake --build build
```

The same CMake package config is present in the movable source-tree archive:

```bash
make package-c-api-stage
mkdir -p /tmp/rtdl-c-api-consume
tar -C /tmp/rtdl-c-api-consume -xzf build/rtdl-c-api-stage-0.1.3.tar.gz
cmake -S . -B build -DCMAKE_PREFIX_PATH="/tmp/rtdl-c-api-consume/rtdl-c-api-stage-0.1.3"
cmake --build build
```

For direct-link clients:

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

For the host external-runtime metadata example:

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

For the CUDA buffer metadata descriptor-only example:

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

For the Python `ctypes` CUDA buffer metadata path:

```bash
python3 build/c_api_stage/examples/python_ctypes_cuda_buffer_metadata_client.py \
  build/c_api_stage/lib/librtdl_c_api.so
```

Expected output:

```text
python_ctypes_cuda_metadata_shape=(3,4) query_route_rejected=invalid argument
```

For the Python `ctypes` DLPack-like buffer metadata path:

```bash
python3 build/c_api_stage/examples/python_ctypes_dlpack_like_metadata_client.py \
  build/c_api_stage/lib/librtdl_c_api.so
```

Expected output:

```text
python_ctypes_dlpack_like_metadata_shape=(2,3) query_route_rejected=invalid argument
```

For a minimal language-binding style client without writing C/C++:

```bash
python3 build/c_api_stage/examples/python_ctypes_client.py \
  build/c_api_stage/lib/librtdl_c_api.so
```

Expected output:

```text
python_ctypes_ok 0.1.3 ok
```

For the same Python `ctypes` path running the current host AABB2 query route:

```bash
python3 build/c_api_stage/examples/python_ctypes_aabb2_query_client.py \
  build/c_api_stage/lib/librtdl_c_api.so
```

Expected output:

```text
python_ctypes_hit_count=1 first_pair=(0,0)
```

## Boundary

- This is a source-tree C client example for the V3 draft C ABI.
- `package-c-api-stage` produces a source-tree staging archive, not an installed
  SDK or stable release artifact, even though the archive carries staged
  `pkg-config` and CMake metadata.
- `stage-c-api-prefix` produces a DESTDIR/prefix-style staging layout, not a
  privileged system install, package-manager artifact, stable SDK, or release
  claim.
- It validates only host `F32` AABB2 overlap through `librtdl_c_api`.
- The Python `ctypes` example validates version/capability/context lifecycle
  calls only; it is not a generated Python package or complete binding.
- The Python `ctypes` AABB2 query example validates host buffer import, index
  build, query execute, result export, and handle cleanup for the current host
  AABB2 route only.
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
- It is not an OptiX, Embree, device-buffer query, packaged-SDK, or frozen-ABI claim.
