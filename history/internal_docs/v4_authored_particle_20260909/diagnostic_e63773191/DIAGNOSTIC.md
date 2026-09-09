# Public source-authored Particle exploratory diagnostic

Date: 2026-09-09 UTC. This directory preserves an adverse exploratory run. It
is not a preregistered or formal performance transaction and must not be pooled
with a later run.

## Exact scope

- Source commit: `e63773191074a5a67a5e2d79bee2b4f3c019e8ca`.
- Source tree: `3e5204af59e6968b90998af7386262e3eb1163d0`.
- GPU: NVIDIA RTX 4000 Ada Generation, CC 8.9,
  `GPU-2a00572b-6cef-b9e6-db0a-c127783a5d46`.
- Driver: 550.127.05.
- Native provider SHA-256:
  `94d9e42be75c86c3186dac1d2a280873206698ea620f5666b83e4d49ce00686d`.
- Input manifest SHA-256:
  `c6678099ecff9581726781a765213d5b0890f20ada70561b09dd6dd94a4009af`.
- Both arms produced the same complete 5,000-by-3 U32 output SHA-256:
  `452ec9df2d8ee3c3a274dcbe4e175df305380f25793472e05da448e9556ed73b`.

The application-owned output is `(face_id, selected_cell, neighbor_cell)`.
The RTDL arm executed the public `verify -> compile -> materialize -> prepare
-> execute` lifecycle and returned a bound OptiX traversal receipt. The
PyOptiX arm used separately handwritten CUDA, precompiled PTX, public PyOptiX
orchestration, `PREFER_FAST_TRACE`, disabled any-hit, and native closest-hit.

## Commands

Environment common to both workers:

```sh
cd /tmp/rtdl-authored-e637
export PYTHONPATH=/tmp/rtdl-authored-e637/src:/tmp/rtdl-authored-e637:/tmp/rtdl-crossgpu/pyoptix-build/installed
export CUDA_VISIBLE_DEVICES=0
export NUMBA_CUDA_USE_NVIDIA_BINDING=1
```

RTDL:

```sh
export RTDL_OPTIX_LIB=/tmp/rtdl-crossgpu/native/librtdl_optix.so
/tmp/rtdl-crossgpu/venv/bin/python scripts/v4_authored_particle_worker.py \
  --arm rtdl --data-root /tmp/rtdl-authored-data \
  --native /tmp/rtdl-crossgpu/native/librtdl_optix.so \
  --optix-include /tmp/rtdl-crossgpu/optix-dev/include \
  --cuda-include /usr/local/cuda-12.8/targets/x86_64-linux/include \
  --compute-capability 8.9 --warmups 1 --samples 3
```

PyOptiX:

```sh
/tmp/rtdl-crossgpu/venv/bin/python scripts/v4_authored_particle_worker.py \
  --arm pyoptix --data-root /tmp/rtdl-authored-data \
  --pyoptix-ptx /tmp/rtdl-authored-particle/face_first_pyoptix.ptx \
  --warmups 1 --samples 3
```

Both commands exited zero. The RTDL median was 832,998 ns and the PyOptiX
median was 369,672 ns. Their unregistered ratio is
`2.253343504512108`. This misses the engineering target and is retained as an
adverse diagnostic.

## Diagnosis and evidence limit

A separate, unregistered within-process hierarchy probe measured RTDL public
execute at 793,646.5 ns, the runtime owner with an ordinary Nx7 batch at
662,417.5 ns, and the runtime owner with its existing immutable prepared query
batch at 326,121.0 ns. This localizes most avoidable overhead to query-column
rematerialization and the public receipt-validation representation, not to a
Particle-specific computation. Those three numbers are diagnostic only and no
raw probe file was retained.

The worker retains only the last execution's receipt/counter projection and
does not export the generated RTDL leaf PTX, wrapper, physical plan, every
sample's receipt, or complete output bytes. The included PTX is only the
PyOptiX arm. Therefore these files establish exploratory correctness and a
performance direction, not formal language-performance evidence. A successor
must use a new committed identity and retain the missing artifacts.

The generated input arrays came from the exact author Git commit and CRLF VTU
bytes used by the historical authority, but this manifest embeds a different
absolute source path. It consequently has a new manifest identity and is not
relabeled as the historical input manifest.

## Preserved member identities

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `RTDL_DIAGNOSTIC.json` | 1,734 | `745a671208f1431c6a9e27a920af8e6481ac2d4bcca8a4a762ad49be36e3bd16` |
| `PYOPTIX_DIAGNOSTIC.json` | 2,038 | `c5dcdd6b720b69126877a70d2eede964d7e0add19c0c29d1d00c98639a8f49ca` |
| `RTDL_PROFILE_RUN.json` | 2,073 | `1540b1f7caedb554212b1626da515a78f8e06d731efc22f0ac8e36a8217f98ca` |
| `RTDL_PROFILE.pstats` | 336,735 | `a9f3839a962a05361dd0f92547c320979623f6c7aa0a7b66144c6a7c725e6336` |
| `PYOPTIX_FACE_FIRST.ptx` | 8,210 | `35429df1300683837862fe03772ea89d7520e9dc0d368fd78a21fbe87db2ad70` |
| `PARTICLE_INPUT_MANIFEST.json` | 2,507 | `c6678099ecff9581726781a765213d5b0890f20ada70561b09dd6dd94a4009af` |
