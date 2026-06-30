# Goal2577 LibRTS Authors-Code Mutation Evidence

## Scope

The public `rtspatial_exec` binary covers insert plus query timing, but the
authors library also exposes `Insert`, `Update`, and `Delete` APIs. This goal
uses the authors' own GTest suite to verify mutation behavior without adding any
RTDL native mutation path.

## Environment

| Field | Value |
| --- | --- |
| Pod SSH | `root@203.57.40.169 -p 10212 -i ~/.ssh/id_ed25519_rtdl_codex` |
| Pod host | `2f2405dbb885` |
| GPU | NVIDIA RTX A5000 |
| Driver | `565.57.01` |
| RTSpatial source | `52509e8022abeab722f5a9a89d1917e8b481defe` |
| OptiX SDK | `8.1.0` |
| CUDA toolkit | `12.6.85` |
| Test dependency | `libgtest-dev` |

## Build

```bash
cmake -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_EXAMPLES=OFF \
  -DBUILD_TESTS=ON \
  -DCMAKE_CUDA_COMPILER=/usr/local/cuda-12.6/bin/nvcc \
  -DCUDAToolkit_ROOT=/usr/local/cuda-12.6 \
  -DCMAKE_CUDA_ARCHITECTURES=86 \
  -DOptiX_INSTALL_DIR=/opt/optix/NVIDIA-OptiX-SDK-8.1.0-linux64-x86_64 ..
cmake --build . -j$(nproc)
```

## Result

Raw outputs:

- `docs/reports/librts_pod_raw/goal2577_rtspatial_mutation_tests.json`
- `docs/reports/librts_pod_raw/goal2577_rtspatial_mutation_tests.txt`

| Test | Meaning | Time | Result |
| --- | --- | ---: | --- |
| `EnvelopeQueries.fp32_intersects_envelope_batch_update` | 100k indexed boxes inserted in 10 batches, then 5% update batch; range-intersects count matches rebuild oracle | `0.658s` | passed |
| `EnvelopeQueries.fp32_test_delete` | delete one indexed envelope and re-query range-intersects | `0.115s` | passed |
| `EnvelopeQueries.fp32_test_delete_compact` | delete one indexed envelope with `compact=true` and re-query range-intersects | `0.107s` | passed |

Total: 3 tests, 0 failures, 0 errors.

## Interpretation

This gives narrow authors-code evidence that mutable update/delete behavior is
implemented and passes the authors' correctness tests on the same pod/toolchain
used for the Goal2575 query timing runs.

It does not time RTDL, does not add an RTDL native mutation primitive, and does
not reproduce the full LibRTS paper mutation-performance evaluation.

## Claim Boundary

- Authors-code mutation correctness evidence only.
- Not an RTDL native mutation primitive.
- Not an RTDL performance claim.
- Not full LibRTS paper reproduction.
