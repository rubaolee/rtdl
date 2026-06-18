# V3.0 C ABI Staging Contract

Status: draft source-tree staging contract for V3 embeddability. This is not a
packaged SDK, installer, stable ABI, or release artifact.

Run this from the repository root:

```bash
make stage-c-api
```

The target first builds `build/librtdl_c_api.*`, then creates
`build/c_api_stage` with:

- `include/rtdl/rtdl.h`
- `lib/librtdl_c_api.*`
- `lib/pkgconfig/rtdl-c-api.pc`
- `share/rtdl/v3_0_c_abi_symbol_manifest.json`
- `share/rtdl/README.md`
- `examples/c_api_aabb2_overlap_client.c`
- `examples/c_api_direct_link_client.c`
- `examples/c_api_host_runtime_client.c`
- `examples/c_api_cuda_buffer_metadata_client.c`
- `examples/python_ctypes_client.py`
- `examples/python_ctypes_aabb2_query_client.py`

The staged manifest is copied from the current draft source-tree manifest,
currently `docs/learn/v3_0_c_abi_symbol_manifest_v0_1_3.json`.

To create a movable archive of the same source-tree stage:

```bash
make package-c-api-stage
```

This writes `build/rtdl-c-api-stage-0.1.3.tar.gz`. The archive is a convenient
source-tree staging package, not a system install, package-manager artifact, or
stable SDK.

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
  directories; it is still not an installed SDK.
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
- No install prefix, package manager artifact, Python wheel, stable binary
  compatibility, OptiX/Embree C ABI query, device-buffer query route, or
  performance wording is authorized.
