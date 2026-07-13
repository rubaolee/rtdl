# LibRTS Author Patches

No author patch is authorized or applied in Goal5453.

Future compatibility patches must distinguish:

- build/toolchain compatibility;
- comparator output instrumentation;
- algorithmic changes, which are forbidden in an AuthorOfficial comparison
  unless separately disclosed and reviewed.

Goal5454 uses a build-only CUDA architecture compatibility patch for the local
Linux GTX 1070. It does not change query semantics.

Goal5460 uses a one-line OptiX update-buffer correction in
`updateInstanceAccel`: the pinned author code allocates
`tempUpdateSizeInBytes` but passes `tempSizeInBytes` to `optixAccelBuild`.
OptiX rejects that undersized buffer on the local Linux mutation probe. The
patch passes the already allocated update size and does not change mutation or
query semantics.

Goal5464 uses `goal5464_spatialquerybenchmark_pip_only_CMakeLists.txt` to build
only the AE-pinned PIP executable. The upstream benchmark CMake requires CGAL,
GLIN, ParGeo, and unrelated query targets even though PIP does not use them.
The wrapper compiles the exact author `pip.cpp`, `pip_query.cu`, and
`pip_handler.h` sources against AE-pinned RTSpatial. It changes no PIP logic;
`CUDA_ARCHITECTURES=61` is the disclosed GTX 1070 build compatibility setting.
The accompanying `goal5464_cuda12_compat/amxtileintrin.h` is an empty shim for
an unused host-only Intel AMX header that nvcc 12.0 cannot parse through Boost
on GCC 12/13. The PIP code does not call AMX intrinsics.

Goal5466 uses `goal5466_spatialquerybenchmark_gen_only_CMakeLists.txt` to build
the pinned author's `src/gen/gen.cpp` and `src/flags.cpp` without unrelated
benchmark targets. Repeated generation with seed `0` produces the committed
100K query file hash exactly.

Goal5467 applies `goal5467_export_author_pip_rows.patch` only to a separate
comparator build. The patch copies the already collected result queue to a CSV
path named by `LIBRTS_PIP_ROW_DUMP`; it does not change `pnpoly`, candidate
traversal, queue append, or the public result count. The unmodified and
instrumented binaries must report the same count before pair rows are accepted.
