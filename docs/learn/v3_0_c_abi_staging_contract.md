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

The staged manifest is copied from the current draft source-tree manifest,
currently `docs/learn/v3_0_c_abi_symbol_manifest_v0_1_3.json`.

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
```

## Boundary

- This is a source-tree staging bundle only.
- The only validated route remains host `F32` AABB2 overlap through the draft C
  ABI.
- No install prefix, package manager artifact, Python wheel, stable binary
  compatibility, OptiX/Embree C ABI query, device-buffer route, or performance
  wording is authorized.
