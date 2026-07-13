# Goal5019: Native Thrust Lexsort Probe For Section 5.7 Columnar Route

## Purpose

Answer the owner challenge directly: nobody forbids using CUB/Thrust.  The
right test is to add a generic native CUDA/Thrust lexicographic sort helper,
wire it into the RayJoin Section 5.7 columnar route as an opt-in backend, and
measure it against the existing Numba bitonic device sort on the same top4
County x Zipcode representative workload.

This goal is not a Layer-4 fusion attempt and not a RayJoin-specific native
kernel.  It tests one generic continuation primitive: sort four device-resident
key columns lexicographically.

## Implementation

Changed files:

- `src/native/optix/rtdl_optix_cuda_helpers.cu`
  - Added `rtdl_cuda_sort_i64_f64_i64_i64_lex`.
  - Uses Thrust zip-iterator sort over `(int64 edge, double dist, int64 tie, int64 order)`.
  - Generic name and generic key-column contract; no overlay/output-chain semantics.

- `src/rtdsl/optix_runtime.py`
  - Added `run_cuda_lexsort_i64_f64_i64_i64_device(...)`.
  - Uses optional native symbol lookup and existing `_check_status`.
  - Fails closed when the rebuilt backend does not export the symbol.

- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`
  - Added `--native-lexsort` opt-in flag.
  - Default remains the old Numba bitonic implementation.
  - Emits `xsect_sort_backends` and claim-boundary backend fields in JSON.
  - Keeps CPU longdouble order validation available through `--validate-device-order`.

- `tests/goal5019_native_lexsort_bridge_test.py`
  - Structural guard that the native helper is generic, optional, and not default.

## Verification

Local:

```text
PYTHONPATH=src py -3 -m unittest tests.goal5019_native_lexsort_bridge_test
Ran 3 tests in 0.047s
OK

PYTHONPATH=src py -3 -m py_compile src/rtdsl/optix_runtime.py Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
OK
```

POD:

```text
PYTHONPATH=src python -m unittest tests.goal5019_native_lexsort_bridge_test
Ran 3 tests in 0.009s
OK

make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk-8.1 CUDA_PREFIX=/usr/local/cuda-12.8
OK
```

The build proves the current POD has the required CUDA/Thrust headers and toolchain.

## POD Measurement

Workload:

- Pair: top4 County x Zipcode representative CDBs.
- Route: writer-free numeric binary, `--device-columnar`, bounded exact LSI device columns, point-location device face columns, fast scaled-point host pack, compiled group.
- Correctness gate: `--validate-device-order` on every run.
- Structural anchors:
  - `lsi_row_count = 428322`
  - `descriptor_pair_count = 15014`
  - CPU longdouble sort order validation: both sides `true`.

| Run | Backend | writer_free_hot_sec | sort_map0 | sort_map1 | sort total |
|---|---:|---:|---:|---:|---:|
| bitonic warm | Numba bitonic | 3.631654 | 0.032050 | 0.093283 | 0.125333 |
| native first | native Thrust | 3.628723 | 0.100679 | 0.080773 | 0.181451 |
| native warm | native Thrust | 3.613519 | 0.024220 | 0.081317 | 0.105537 |

Result artifacts:

- `history/internal_docs/rtdl_goal5019_bitonic_warm_top4.json`
- `history/internal_docs/rtdl_goal5019_native_thrust_top4.json`
- `history/internal_docs/rtdl_goal5019_native_thrust_warm_top4.json`

## Interpretation

The owner was right that native CUB/Thrust was not forbidden.  We implemented
and measured it.  The result is useful but small:

- Correctness: passed.  Native Thrust order matches the CPU longdouble reference.
- Genericity: acceptable.  The native helper is a generic device-column lexsort,
  not a RayJoin overlay kernel.
- Performance: warm native Thrust reduced sort total from about `0.125s` to
  about `0.106s`, a roughly `0.020s` improvement on this workload.

This is not a 10x lever.  Sorting is no longer a large enough component in the
current top4 route for a generic sort backend swap to change the headline
number.  The remaining large costs are still:

- LSI producer setup/ensure around `~2.7s` in fresh top4 runs.
- Point-location prepare / duplicate canonicalization / range construction.
- Host-side compiled carrier and remaining non-resident continuation costs.

## Decision

Recommended status:

```text
completed_native_thrust_lexsort_probe_correct_small_win_keep_opt_in
```

Do not promote native Thrust lexsort to the default yet.  Keep it behind
`--native-lexsort` until broader inputs show a consistent win.  The correct next
performance target is not sort; it is the larger prepared-workspace and
point-location preparation costs.

## Non-Claims

This goal does not claim:

- 10x improvement.
- Author parity.
- Full device-resident overlay.
- Layer-4 fusion.
- A RayJoin-specific native kernel.
- That native Thrust should become the default route.
